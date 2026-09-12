"""
Build the mountain altitude profiles and attach them to the right tours.

    python manage.py seed_climbs

Safe to re-run. Routes are matched to packages on the package's own `route`
field, falling back to a title match for mountains with only one way up.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from tours.data.climbs import CLIMBS, TITLE_HINTS
from tours.models import ClimbRoute, ClimbStage, Package


class Command(BaseCommand):
    help = "Create mountain climb profiles and link them to packages."

    @transaction.atomic
    def handle(self, *args, **options):
        for order, spec in enumerate(CLIMBS):
            route, _ = ClimbRoute.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "slug": slugify(spec["name"]),
                    "mountain": spec["mountain"],
                    "summary": spec["summary"],
                    "order": order,
                },
            )
            route.stages.all().delete()
            for i, (name, altitude, day) in enumerate(spec["stages"]):
                ClimbStage.objects.create(
                    route=route, order=i, name=name, altitude_m=altitude, day=day)

            summit = route.summit()
            self.stdout.write(
                f"  {route.mountain:<18} {route.name:<20} "
                f"{route.stages.count():>2} camps, summit {summit.altitude_m} m")

        # --- attach to packages ------------------------------------------
        Package.objects.update(climb_route=None)
        linked = 0

        for route in ClimbRoute.objects.all():
            matches = Package.objects.filter(route=route.name)
            if matches.exists():
                linked += matches.update(climb_route=route)
                continue

            for hint in TITLE_HINTS.get(route.name, []):
                matches = Package.objects.filter(title__icontains=hint, route="")
                linked += matches.update(climb_route=route)

        self.stdout.write("\n  linked to packages:")
        for p in Package.objects.filter(climb_route__isnull=False).order_by("title"):
            self.stdout.write(f"    {p.climb_route.name:<20} {p.title}")

        self.stdout.write(self.style.SUCCESS(
            f"\n{ClimbRoute.objects.count()} routes, "
            f"{ClimbStage.objects.count()} camps, {linked} packages linked."))
