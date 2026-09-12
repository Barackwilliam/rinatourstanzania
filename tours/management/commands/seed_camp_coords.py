"""
Put approximate positions on the Kilimanjaro camps so the route map can draw.

Safe to re-run. It will NOT overwrite a camp whose coordinates a guide has
already verified — the whole point of the exercise is that their corrections
survive a redeploy.

    python manage.py seed_camp_coords
    python manage.py seed_camp_coords --force   # overwrite verified ones too
"""

from django.core.management.base import BaseCommand

from tours.data.kilimanjaro_map import CAMP_COORDS, MERU_STAGES, VERIFIED
from tours.models import ClimbStage


class Command(BaseCommand):
    help = "Seed approximate coordinates for Kilimanjaro camps, huts and gates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Overwrite positions a guide has already verified.")

    def handle(self, *args, **options):
        force = options["force"]
        placed = skipped = protected = unknown = 0
        missing = set()

        for stage in ClimbStage.objects.select_related("route"):
            coords = CAMP_COORDS.get(stage.name)

            if coords is None:
                if stage.name in MERU_STAGES:
                    skipped += 1          # Meru is outside the map box
                else:
                    unknown += 1
                    missing.add(stage.name)
                continue

            if stage.coords_verified and not force:
                protected += 1
                continue

            stage.longitude, stage.latitude = coords
            stage.coords_verified = stage.name in VERIFIED
            stage.save(update_fields=["longitude", "latitude", "coords_verified"])
            placed += 1

        self.stdout.write(f"\n{placed} camps placed.")
        if protected:
            self.stdout.write(
                f"{protected} left alone — already verified by a guide. "
                f"Use --force to overwrite.")
        if skipped:
            self.stdout.write(f"{skipped} Mount Meru stages skipped (off this map).")
        if unknown:
            self.stdout.write(self.style.WARNING(
                f"{unknown} stages have no position and will not plot: "
                + ", ".join(sorted(missing))))

        self.stdout.write(self.style.WARNING(
            "\nThese positions are APPROXIMATE. Only Uhuru Peak and Barafu Camp "
            "come from a published source; the rest are interpolated from the "
            "mountain's layout.\n"
            "Run `manage.py export_camp_coords` to get the list to send to the "
            "guides, then correct them in the admin and tick 'coords verified'."))
