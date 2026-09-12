"""
Put the Kilimanjaro climb prices back to what they were before
`set_climb_price --flat` flattened them all to one figure.

    python manage.py restore_climb_prices           # dry run
    python manage.py restore_climb_prices --apply   # write it

The figures below are the ones the site was actually running, captured from
the command output before the change. They scale with the length of the climb,
which is how they should be: a 9-day route costs more to operate than a 6-day
one.

After restoring, apply the client's $1746 as a FLOOR rather than a flat rate:

    python manage.py set_climb_price --apply

That lifts Marangu, Machame and Umbwe to $1746 and leaves the longer routes
priced above it.

Matched on route keyword plus duration rather than on the full title, because
"Machame" alone is ambiguous — there is a 6-day and a 7-day version at
different prices.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.models import Package

# (keyword in title, duration_days) -> price the site was running
ORIGINAL_PRICES = {
    ("marangu", 6): Decimal("1500.00"),
    ("machame", 6): Decimal("1500.00"),
    ("umbwe", 6): Decimal("1650.00"),
    ("machame", 7): Decimal("1750.00"),
    ("rongai", 7): Decimal("1750.00"),
    ("lemosho", 7): Decimal("1800.00"),
    ("lemosho", 8): Decimal("2000.00"),
    ("northern circuit", 9): Decimal("2200.00"),
}


class Command(BaseCommand):
    help = "Restore Kilimanjaro climb prices flattened by set_climb_price --flat."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Actually write the change. Without this it is a dry run.")

    def handle(self, *args, **options):
        apply_it = options["apply"]

        climbs = list(
            Package.objects
            .filter(climb_route__mountain="Mount Kilimanjaro")
            .order_by("duration_days", "title")
        )

        matched, unmatched = [], []
        for package in climbs:
            title = package.title.lower()
            price = None
            for (keyword, days), value in ORIGINAL_PRICES.items():
                if keyword in title and package.duration_days == days:
                    price = value
                    break
            if price is None:
                unmatched.append(package)
            else:
                matched.append((package, price))

        self.stdout.write("\nRestoring original Kilimanjaro climb prices\n")
        for package, price in matched:
            current = f"${package.price_from}" if package.price_from else "no price"
            marker = "  " if package.price_from == price else "->"
            self.stdout.write(
                f"  {package.duration_days}d  {current:>9} {marker} ${price}   "
                f"{package.title}")

        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"\n{len(unmatched)} climb(s) had no original price on record — "
                f"left untouched, set these by hand in the admin:"))
            for package in unmatched:
                self.stdout.write(self.style.WARNING(
                    f"  {package.duration_days}d  ${package.price_from}   "
                    f"{package.title}"))

        if not apply_it:
            self.stdout.write(self.style.WARNING(
                f"\nDRY RUN — nothing written. Re-run with --apply."))
            return

        with transaction.atomic():
            for package, price in matched:
                package.price_from = price
                package.save(update_fields=["price_from"])

        self.stdout.write(self.style.SUCCESS(
            f"\n{len(matched)} climbs restored."))
        self.stdout.write(
            "\nNow apply the client's figure as a floor instead of a flat rate:\n"
            "    python manage.py set_climb_price --apply")
