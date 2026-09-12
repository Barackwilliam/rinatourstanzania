"""
Add the tours the client asked for after reviewing the first build, and lift
the ones he could not find.

    python manage.py seed_client_requests

Safe to re-run: packages are matched on slug and updated rather than
duplicated. Anything without a price the client has given is created
UNPUBLISHED — an unpublished tour is a gap, a published tour with an invented
price is a complaint.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from tours.data.client_requests import PACKAGES, PROMOTE_DAY_TRIP_KEYWORDS
from tours.models import Category, Destination, Package


class Command(BaseCommand):
    help = "Create the client's newly requested tours and promote existing ones."

    @transaction.atomic
    def handle(self, *args, **options):
        created = updated = 0
        unpriced = []

        for spec in PACKAGES:
            spec = dict(spec)
            slug = spec.pop("slug")
            primary_name = spec.pop("primary_category")
            category_names = spec.pop("categories", [primary_name])
            destination_names = spec.pop("destinations", [])
            needs_pricing = spec.pop("needs_pricing", False)

            try:
                primary = Category.objects.get(name=primary_name)
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"No category named {primary_name!r} — skipping {slug}."))
                continue

            spec["primary_category"] = primary
            # Unpriced tours stay out of sight until someone fills the price in.
            spec["published"] = not needs_pricing
            # Sit near the top of their category so the client can find them.
            spec.setdefault("order", 5)

            package, was_created = Package.objects.update_or_create(
                slug=slug, defaults=spec)

            package.categories.set(
                Category.objects.filter(name__in=category_names) or [primary])
            if destination_names:
                package.destinations.set(
                    Destination.objects.filter(name__in=destination_names))

            created += was_created
            updated += not was_created
            if needs_pricing:
                unpriced.append(package.title)

        # --- Lift the day trips he said were missing ---------------------
        # Find them by keyword rather than exact title — see the note in
        # tours/data/client_requests.py.
        wanted = Q()
        for keyword in PROMOTE_DAY_TRIP_KEYWORDS:
            wanted |= Q(title__icontains=keyword)

        day_trips = Package.objects.filter(duration_days=1)
        to_promote = list(day_trips.filter(wanted).values_list("id", "title"))
        promote_ids = [pk for pk, _title in to_promote]

        # `order` is a PositiveIntegerField, so there is no going below the
        # zero everything already sits at. Push the other day trips down first,
        # then put the named ones at zero — otherwise "promoting" them to 1
        # actually buries them under every untouched tour.
        day_trips.exclude(id__in=promote_ids).filter(order=0).update(order=5)
        promoted = day_trips.filter(id__in=promote_ids).update(order=0)

        if to_promote:
            self.stdout.write("\nLifted to the top of the day trips:")
            for _pk, title in sorted(to_promote, key=lambda t: t[1]):
                self.stdout.write(f"  - {title}")
        else:
            self.stdout.write(self.style.ERROR(
                "\nNo day trips matched any of the promote keywords. Check "
                "that the tours were imported: manage.py import_packages"))

        self.stdout.write(
            f"\n{created} tours created, {updated} updated, "
            f"{promoted} existing day trips lifted.")

        if unpriced:
            self.stdout.write(self.style.WARNING(
                "\nCreated UNPUBLISHED because we have no price from the "
                "client yet:"))
            for title in unpriced:
                self.stdout.write(f"  - {title}")
            self.stdout.write(
                "\nSet price_from in the admin and tick 'published' on each.")
