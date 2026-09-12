"""
Set the starting price for Kilimanjaro climbs.

    python manage.py set_climb_price                 # dry run — shows, changes nothing
    python manage.py set_climb_price --apply         # raise anything below the floor
    python manage.py set_climb_price --apply --flat  # set EVERY climb to the figure

Two behaviours, because "the price starts from $1746" and "every climb costs
$1746" are different instructions and the difference is money:

  floor (default)  Climbs priced below the figure come up to it. Climbs
                   already above keep their price. The cheapest Kilimanjaro
                   climb becomes $1746, which is what a "from" price means.

  --flat           Every Kilimanjaro climb is set to the figure, including the
                   long ones. This CUTS the price of the 8- and 9-day routes,
                   which are longer, cost more to run and are currently priced
                   higher. Only use it if that is genuinely intended.

Dry run is the default on purpose. This edits live prices in bulk.

Only touches packages linked to a Kilimanjaro ClimbRoute. Day hikes in the
foothills have "Kilimanjaro" in the title but are not climbs, and matching on
the title would have repriced an $80 walk to $1746.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.models import Package

DEFAULT_PRICE = Decimal("1746.00")


class Command(BaseCommand):
    help = "Set the starting price for Mount Kilimanjaro climbing packages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--price", type=Decimal, default=DEFAULT_PRICE,
            help=f"The figure to use. Default {DEFAULT_PRICE}.")
        parser.add_argument(
            "--apply", action="store_true",
            help="Actually write the change. Without this it is a dry run.")
        parser.add_argument(
            "--flat", action="store_true",
            help="Set every climb to the figure, not just the ones below it. "
                 "This lowers the long routes — read the warning.")
        parser.add_argument(
            "--mountain", default="Mount Kilimanjaro",
            help="Which mountain. Default 'Mount Kilimanjaro'. Meru is left "
                 "alone unless you name it.")

    def handle(self, *args, **options):
        price = options["price"]
        apply_it = options["apply"]
        flat = options["flat"]
        mountain = options["mountain"]

        climbs = (
            Package.objects
            .filter(climb_route__mountain=mountain)
            .select_related("climb_route")
            .order_by("duration_days", "title")
        )

        if not climbs:
            self.stdout.write(self.style.ERROR(
                f"No packages are linked to a {mountain} climb route. Check "
                f"`manage.py seed_climbs` has run."))
            return

        changes, unchanged, cuts = [], [], []
        for p in climbs:
            old = p.price_from
            if flat or old is None or old < price:
                if old is not None and old > price:
                    cuts.append((p, old))
                changes.append((p, old))
            else:
                unchanged.append((p, old))

        self.stdout.write(f"\n{mountain} climbs — price {'' if flat else 'floor '}"
                          f"${price}\n")

        for p, old in changes:
            was = f"${old}" if old is not None else "no price"
            self.stdout.write(f"  {p.duration_days}d  {was:>9} -> ${price}   {p.title}")
        for p, old in unchanged:
            self.stdout.write(self.style.SUCCESS(
                f"  {p.duration_days}d  ${old:>8} unchanged   {p.title}"))

        if cuts:
            self.stdout.write(self.style.WARNING(
                f"\nWARNING: this LOWERS the price of {len(cuts)} longer "
                f"route(s):"))
            for p, old in cuts:
                self.stdout.write(self.style.WARNING(
                    f"  {p.duration_days} days  ${old} -> ${price}   {p.title}"))
            self.stdout.write(self.style.WARNING(
                "A 9-day climb costs more to run than a 6-day one: more park "
                "fees, more crew days, more food. Confirm with the client "
                "before cutting these."))

        if not apply_it:
            self.stdout.write(self.style.WARNING(
                f"\nDRY RUN — nothing written. {len(changes)} would change, "
                f"{len(unchanged)} would stay.\n"
                f"Re-run with --apply to write it."))
            return

        with transaction.atomic():
            for p, _old in changes:
                p.price_from = price
                p.price_basis = "person"
                p.save(update_fields=["price_from", "price_basis"])

        self.stdout.write(self.style.SUCCESS(
            f"\n{len(changes)} climbs updated, {len(unchanged)} left as they were."))
