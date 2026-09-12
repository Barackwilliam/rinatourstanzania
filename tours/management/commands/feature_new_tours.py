"""
Put the tours added in the latest round onto the homepage.

    python manage.py feature_new_tours                       # dry run
    python manage.py feature_new_tours --apply
    python manage.py feature_new_tours --apply --force       # publish unpriced ones too

The homepage shows `featured` tours that are `published`. Three of the four
tours added in the last round are neither, because the client has not given a
price for any of them — they were created unpublished on purpose, so nothing
went live carrying an invented figure.

So this command will NOT publish a tour that still has no price, unless you
pass --force. A tour on the homepage with no price is a dead end for the
visitor and an awkward email for Rina.

Fill the prices in the admin (or with `set_climb_price` for climbs), then run
this.
"""

from django.core.management.base import BaseCommand

from tours.models import Package

# Slugs are generated from titles and vary between imports, so match on
# keywords — see find_package.
NEW_TOUR_KEYWORDS = [
    "bike",
    "moshi town",
    "chemka",
    "maasai boma",
]


class Command(BaseCommand):
    help = "Publish and feature the newly added tours so they show on the homepage."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true",
                            help="Write the change. Without this it is a dry run.")
        parser.add_argument("--force", action="store_true",
                            help="Publish even tours that still have no price.")

    def handle(self, *args, **options):
        apply_it, force = options["apply"], options["force"]

        found = []
        for keyword in NEW_TOUR_KEYWORDS:
            for p in Package.objects.filter(title__icontains=keyword):
                if p not in found:
                    found.append(p)

        if not found:
            self.stdout.write(self.style.ERROR(
                "No matching tours. Run: python manage.py seed_client_requests"))
            return

        ready = [p for p in found if p.price_from]
        unpriced = [p for p in found if not p.price_from]

        self.stdout.write("")
        for p in ready:
            self.stdout.write(
                f"  ${p.price_from:>7.0f}  -> featured on the homepage   {p.title}")
        for p in unpriced:
            mark = "will publish" if force else "SKIPPED"
            self.stdout.write(self.style.WARNING(
                f"  no price  -> {mark:<25} {p.title}"))

        if unpriced and not force:
            self.stdout.write(self.style.WARNING(
                f"\n{len(unpriced)} tour(s) have no price and stay hidden. A tour "
                f"on the homepage with no price gives the visitor nothing to act "
                f"on.\nAsk the client for the figures, set price_from in the "
                f"admin, then re-run. Use --force only if you want them live "
                f"without one."))

        targets = found if force else ready
        if not apply_it:
            self.stdout.write(self.style.WARNING(
                f"\nDRY RUN — nothing written. {len(targets)} tour(s) would go "
                f"onto the homepage.\nRe-run with --apply."))
            return

        for p in targets:
            p.published = True
            p.featured = True
            p.order = 0
            p.save(update_fields=["published", "featured", "order"])

        self.stdout.write(self.style.SUCCESS(
            f"\n{len(targets)} tour(s) published and featured."))
