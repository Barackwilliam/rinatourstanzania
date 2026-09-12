"""
Print the camp list as CSV, for sending to the mountain guides to check.

    python manage.py export_camp_coords > camps.csv

Open it in Excel, send it to whoever guides the climbs, and have them fill in
the last column for any position that is wrong. Then correct those camps in the
admin and tick 'coords verified' so the map stops flagging them.
"""

import csv
import sys

from django.core.management.base import BaseCommand

from tours.models import ClimbStage


class Command(BaseCommand):
    help = "Export climb camp coordinates as CSV for guides to verify."

    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout)
        writer.writerow([
            "Route", "Day", "Camp", "Altitude (m)",
            "Latitude (our guess)", "Longitude (our guess)",
            "Verified", "CORRECT POSITION (guide fills in)",
        ])

        seen = set()
        for stage in ClimbStage.objects.select_related("route").order_by(
                "route__order", "order"):
            # One row per camp per route; a camp revisited on the descent does
            # not need checking twice.
            key = (stage.route_id, stage.name)
            if key in seen:
                continue
            seen.add(key)

            writer.writerow([
                stage.route.name,
                stage.day or "",
                stage.name,
                stage.altitude_m,
                stage.latitude if stage.latitude is not None else "",
                stage.longitude if stage.longitude is not None else "",
                "yes" if stage.coords_verified else "no",
                "",
            ])
