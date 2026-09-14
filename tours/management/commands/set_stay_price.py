"""
Set the guest house rate.

    python manage.py set_stay_price            # dry run
    python manage.py set_stay_price --apply
    python manage.py set_stay_price --apply --price 95

The figure appears on the stay page, in the homepage band and anywhere else
the accommodation is quoted, so it is one number in one place rather than
something to hunt for in the admin.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from tours.models import Accommodation

DEFAULT_PRICE = Decimal("80.00")


class Command(BaseCommand):
    help = "Set the per-person nightly rate for the guest house."

    def add_arguments(self, parser):
        parser.add_argument("--price", type=Decimal, default=DEFAULT_PRICE)
        parser.add_argument("--apply", action="store_true",
                            help="Write the change. Without this it is a dry run.")

    def handle(self, *args, **options):
        price, apply_it = options["price"], options["apply"]

        stays = Accommodation.objects.all()
        if not stays:
            self.stdout.write(self.style.ERROR(
                "No accommodation on record. Run: manage.py seed_stay"))
            return

        for stay in stays:
            was = f"${stay.price_from}" if stay.price_from else "no price"
            self.stdout.write(f"  {was:>10} -> ${price}   {stay.name}")

        if not apply_it:
            self.stdout.write(self.style.WARNING(
                "\nDRY RUN — nothing written. Re-run with --apply."))
            return

        for stay in stays:
            stay.price_from = price
            stay.save(update_fields=["price_from"])

        self.stdout.write(self.style.SUCCESS(
            f"\nRate set to ${price} per person."))
