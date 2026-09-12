"""
Load the guest house and the transfer price list.

    python manage.py seed_stay

Reads tours/data/stay.py. Re-running updates in place; anything edited in the
admin that is not in that file is left alone.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.data.stay import ACCOMMODATION, TRANSFERS
from tours.models import Accommodation, AccommodationFeature, TransferService


def _dec(value):
    return Decimal(str(value)) if value is not None else None


class Command(BaseCommand):
    help = "Create the accommodation entry and the priced transfer services."

    @transaction.atomic
    def handle(self, *args, **options):
        spec = ACCOMMODATION
        stay, _ = Accommodation.objects.update_or_create(
            slug=spec["slug"],
            defaults={
                "name": spec["name"],
                "tagline": spec["tagline"],
                "location": spec["location"],
                "description": spec["description"],
                "price_from": _dec(spec["price_from"]),
                "currency": spec["currency"],
                "board_basis": spec["board_basis"],
                "active": True,
            },
        )
        stay.features.all().delete()
        for i, (title, detail) in enumerate(spec["features"]):
            AccommodationFeature.objects.create(
                accommodation=stay, title=title, detail=detail, order=i)

        self.stdout.write(f"  {stay.name} — {stay.price_display()}")
        self.stdout.write(f"  {stay.features.count()} features")

        self.stdout.write("\n  transfers:")
        for order, t in enumerate(TRANSFERS):
            service, _ = TransferService.objects.update_or_create(
                slug=t["slug"],
                defaults={
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "route_from": t.get("route_from", ""),
                    "route_to": t.get("route_to", ""),
                    "distance_km": t.get("distance_km"),
                    "duration_text": t.get("duration_text", ""),
                    "price_from": _dec(t.get("price_from")),
                    "price_to": _dec(t.get("price_to")),
                    "price_basis": t.get("price_basis", "trip"),
                    "icon": t.get("icon", ""),
                    "order": order,
                    "active": True,
                },
            )
            self.stdout.write(f"    {service.name:<32} {service.price_display()}")

        self.stdout.write(self.style.SUCCESS(
            f"\n1 accommodation, {TransferService.objects.count()} transfer services."))
