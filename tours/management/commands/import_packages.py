"""
Load the client's tour content into the database.

    python manage.py import_packages            # create/update everything
    python manage.py import_packages --reset    # wipe tours first, then load

Reads tours/data/packages.json and categories.json, which are produced from the
client's original text files by content/parse.py. Re-running is safe: packages
are matched on slug and updated in place, so a corrected export can simply be
re-imported without creating duplicates.
"""

import json
import re
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from tours.data.destinations import CANONICAL, IGNORE, lookup
from tours.models import Category, Destination, ItineraryDay, Package

DATA = Path(__file__).resolve().parent.parent.parent / "data"

BASIS_MAP = {
    "per person": "person",
    "per couple": "couple",
    "per adult": "adult",
    "per private boat": "boat",
    "per group": "group",
    "per vehicle": "vehicle",
}

# Durations the client expressed in hours rather than days.
HOUR_PATTERNS = re.compile(r"(hour|minute|half day)", re.I)


class Command(BaseCommand):
    help = "Import tour packages, categories and destinations from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Delete existing categories, destinations and packages first.")

    @transaction.atomic
    def handle(self, *args, **options):
        packages = json.loads((DATA / "packages.json").read_text(encoding="utf-8"))
        cat_blocks = json.loads((DATA / "categories.json").read_text(encoding="utf-8"))

        if options["reset"]:
            ItineraryDay.objects.all().delete()
            Package.objects.all().delete()
            Destination.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing tour content deleted."))

        categories = self._load_categories(packages, cat_blocks)
        destinations = self._load_destinations()
        self._load_packages(packages, categories, destinations)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"{Category.objects.count()} categories, "
            f"{Destination.objects.count()} destinations, "
            f"{Package.objects.count()} packages, "
            f"{ItineraryDay.objects.count()} itinerary days."
        ))
        incomplete = [p for p in Package.objects.all() if not p.is_complete()]
        if incomplete:
            self.stdout.write(self.style.WARNING(
                f"\n{len(incomplete)} packages are missing Includes/Excludes and are "
                f"flagged 'not ready to sell' in the admin. They are still published — "
                f"untick 'published' on any you would rather hide until the client "
                f"supplies the missing copy."
            ))

    @staticmethod
    def _split_destination(raw, table):
        """Yield the pieces of a destination string that should be looked up."""
        raw = raw.strip()
        if raw.lower() in table or raw in IGNORE:
            return [raw]
        parts = []
        for chunk in re.split(r"\s*/\s*", raw):
            chunk = chunk.strip()
            if chunk.lower() in table or chunk in IGNORE:
                parts.append(chunk)
            else:
                parts += [c.strip() for c in re.split(r"\s+&\s+", chunk)]
        return parts

    # ------------------------------------------------------------------ parts
    # One bead colour per category, drawn from a Maasai beadwork palette.
    # These carry through to the navigation menu and the category tiles.
    BEAD_COLOURS = [
        "#B23A2E",  # red
        "#2E7D4F",  # green
        "#2B5DA8",  # blue
        "#DE8B24",  # orange
        "#7A4E9C",  # violet
        "#00767F",  # teal
        "#17140F",  # black
    ]

    def _load_categories(self, packages, cat_blocks):
        blocks = {c.get("name"): c for c in cat_blocks if c.get("name")}
        names = []
        for p in packages:
            if p["category"] and p["category"] not in names:
                names.append(p["category"])

        out = {}
        for i, name in enumerate(names):
            block = blocks.get(name, {})
            slug = block.get("slug") or slugify(name.replace("/", " "))
            cat, _ = Category.objects.update_or_create(
                name=name,
                defaults={
                    "slug": slug,
                    "code": block.get("code", ""),
                    "description": block.get("description", ""),
                    "bead_colour": self.BEAD_COLOURS[i % len(self.BEAD_COLOURS)],
                    "order": i,
                },
            )
            out[name] = cat
            self.stdout.write(f"  category  {name}")
        return out

    def _load_destinations(self):
        out = {}
        for i, (name, (region, aliases)) in enumerate(CANONICAL.items()):
            dest, _ = Destination.objects.update_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "region": region,
                    "aliases": "\n".join(aliases),
                    "order": i,
                },
            )
            out[name] = dest
        self.stdout.write(f"  {len(out)} canonical destinations")
        return out

    def _load_packages(self, packages, categories, destinations):
        table = lookup()
        unmatched = set()

        # A tour that appears in several categories should be ONE page, not
        # three. Group by slug: first occurrence wins the content, the others
        # only contribute their category.
        grouped = {}
        for p in packages:
            grouped.setdefault(p["slug"], []).append(p)

        for order, (slug, versions) in enumerate(grouped.items()):
            src = versions[0]

            days = src["duration_days"]
            nights = src["duration_nights"]
            duration_text = ""
            if days is None:
                raw = src["duration_raw"].strip()
                if HOUR_PATTERNS.search(raw):
                    duration_text = raw
                elif raw:
                    duration_text = raw

            price = src["price_from"]
            basis = BASIS_MAP.get(src["price_basis"] or "per person", "person")

            primary = categories[src["category"]]

            pkg, _ = Package.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": src["title"].title() if src["title"].isupper() else src["title"],
                    "primary_category": primary,
                    "duration_days": days,
                    "duration_nights": nights,
                    "duration_text": duration_text,
                    "starting_point": src["starting_point"],
                    "route": src["route"],
                    "price_from": Decimal(str(price)) if price is not None else None,
                    "currency": src["currency"] or "USD",
                    "price_basis": basis,
                    "short_description": src["short_description"][:400],
                    "description": src["description"],
                    "highlights": "\n".join(src["highlights"]),
                    "includes": "\n".join(src["includes"]),
                    "excludes": "\n".join(src["excludes"]),
                    "best_for": src["best_for"],
                    "important_note": src["important"],
                    "order": order,
                },
            )

            # every category this tour appeared under
            pkg.categories.set([categories[v["category"]] for v in versions])

            # destinations, normalised
            dests = []
            for v in versions:
                for raw in v["destinations"]:
                    # Try the whole string first — some aliases legitimately
                    # contain "&" (e.g. "Tanga & Amboni Caves"). Only split
                    # when the whole string is unknown.
                    for piece in self._split_destination(raw, table):
                        if not piece or piece in IGNORE:
                            continue
                        canon = table.get(piece.lower())
                        if canon:
                            dests.append(destinations[canon])
                        else:
                            unmatched.add(piece)
            pkg.destinations.set(set(dests))

            # itinerary
            pkg.itinerary_days.all().delete()
            seen = set()
            for day in src["itinerary"]:
                if day["day_number"] in seen:
                    continue
                seen.add(day["day_number"])
                ItineraryDay.objects.create(
                    package=pkg,
                    day_number=day["day_number"],
                    title=day["title"],
                    description=day["description"],
                )

        merged = len(packages) - len(grouped)
        self.stdout.write(
            f"  {len(grouped)} packages "
            f"({merged} duplicate entries merged across categories)")

        if unmatched:
            self.stdout.write(self.style.WARNING(
                "\n  Destination strings with no canonical match — add them to "
                "tours/data/destinations.py or leave them out:"))
            for u in sorted(unmatched):
                self.stdout.write(f"      {u}")
