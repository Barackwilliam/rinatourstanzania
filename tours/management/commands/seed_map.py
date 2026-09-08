"""
Give destinations their coordinates and build the homepage routes map.

    python manage.py seed_map

Safe to re-run: coordinates are only written where they are missing (so a
correction made in the admin is never overwritten), and routes are rebuilt
from scratch each time.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.data.coordinates import COORDINATES, ROUTES
from tours.models import Destination, MapRoute, Package, RouteStop


class Command(BaseCommand):
    help = "Set destination coordinates and rebuild the routes map."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite", action="store_true",
            help="Also overwrite coordinates that have already been set.")

    @transaction.atomic
    def handle(self, *args, **options):
        placed = skipped = 0
        for name, (lat, lon) in COORDINATES.items():
            dest = Destination.objects.filter(name=name).first()
            if not dest:
                self.stdout.write(self.style.WARNING(f"  no destination named {name!r}"))
                continue
            if dest.latitude is not None and not options["overwrite"]:
                skipped += 1
                continue
            dest.latitude, dest.longitude = lat, lon
            dest.save(update_fields=["latitude", "longitude"])
            placed += 1

        missing = Destination.objects.filter(latitude__isnull=True)
        self.stdout.write(f"  {placed} destinations placed, {skipped} already had coordinates")
        if missing.exists():
            self.stdout.write(self.style.WARNING(
                f"  {missing.count()} still have none: "
                + ", ".join(missing.values_list('name', flat=True))))

        RouteStop.objects.all().delete()
        MapRoute.objects.all().delete()

        for order, spec in enumerate(ROUTES):
            package = Package.objects.filter(slug=spec["package_slug"]).first()
            if package is None:
                self.stdout.write(self.style.WARNING(
                    f"  route {spec['name']!r}: no package with slug "
                    f"{spec['package_slug']!r} — legend will not link anywhere"))

            route = MapRoute.objects.create(
                name=spec["name"], slug=spec["slug"], colour=spec["colour"],
                summary=spec["summary"], package=package, order=order,
            )
            for i, dest_name in enumerate(spec["stops"]):
                dest = Destination.objects.filter(name=dest_name).first()
                if dest is None:
                    self.stdout.write(self.style.WARNING(
                        f"    {spec['name']}: unknown stop {dest_name!r}"))
                    continue
                RouteStop.objects.create(route=route, destination=dest, order=i)

            self.stdout.write(
                f"  route  {route.name}  ({route.stops.count()} stops, "
                f"{route.path_length()}px)")

        self.stdout.write(self.style.SUCCESS(
            f"\n{MapRoute.objects.count()} routes, {RouteStop.objects.count()} stops."))
