"""
Bulk-import a folder of photographs, resized and stripped, into the site.

    python manage.py import_photos stay ./photos
    python manage.py import_photos stay ./photos --cover 3
    python manage.py import_photos package 5-days-classic-tanzania-safari ./photos
    python manage.py import_photos destination serengeti-national-park ./photos

Why not just upload through the admin: a photograph off a phone is commonly
4000 px wide and 6-9 MB. Ten of those is most of a Supabase free-tier bucket,
and the page would be unusable on Tanzanian mobile data. This resizes to a
sensible width, re-encodes, and — importantly — strips EXIF.

**EXIF matters.** Phone photographs carry GPS coordinates, the device name and
the exact time. Published as-is, a picture of the guest house tells anyone who
downloads it precisely where the building is. Pillow is asked for the image
data only, so none of that survives.
"""

import io
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageOps

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic", ".heif"}
MAX_WIDTH = 2000
QUALITY = 82


class Command(BaseCommand):
    help = "Resize, strip and import a folder of photographs."

    def add_arguments(self, parser):
        parser.add_argument("target", choices=["stay", "package", "destination"])
        parser.add_argument("params", nargs="*",
                            help="<slug> (except for stay) then <folder>")
        parser.add_argument(
            "--cover", type=int, default=1,
            help="Which photo (1-based, by filename order) becomes the main image.")
        parser.add_argument(
            "--max-width", type=int, default=MAX_WIDTH,
            help=f"Longest edge in pixels. Default {MAX_WIDTH}.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would happen without writing anything.")

    def handle(self, *args, **options):
        target = options["target"]
        rest = list(options["params"])

        if target == "stay":
            if len(rest) != 1:
                raise CommandError("Usage: import_photos stay <folder>")
            slug, folder = None, rest[0]
        else:
            if len(rest) != 2:
                raise CommandError(f"Usage: import_photos {target} <slug> <folder>")
            slug, folder = rest

        folder = Path(folder).expanduser()
        if not folder.is_dir():
            raise CommandError(f"{folder} is not a folder")

        photos = sorted(
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in EXTENSIONS
        )
        if not photos:
            raise CommandError(f"No images found in {folder}")

        owner, gallery_model, gallery_field = self._resolve(target, slug)
        cover_index = max(options["cover"], 1) - 1

        self.stdout.write(f"{len(photos)} photos -> {owner}")
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("dry run — nothing will be saved\n"))

        total_before = total_after = 0
        bigger = []

        for i, path in enumerate(photos):
            try:
                data, size = self._prepare(path, options["max_width"])
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  skipped {path.name}: {exc}"))
                continue

            before = path.stat().st_size
            total_before += before
            total_after += len(data)
            role = "cover" if i == cover_index else "gallery"
            grew = len(data) > before
            line = (f"  {path.name:<32} {before/1024/1024:>5.1f} MB -> "
                    f"{len(data)/1024:>6.0f} KB  {size[0]}x{size[1]}  {role}")
            self.stdout.write(self.style.WARNING(line + "  (grew)") if grew
                              else line)
            if grew:
                bigger.append(path.name)

            if options["dry_run"]:
                continue

            name = f"{path.stem.lower().replace(' ', '-')}.jpg"
            content = ContentFile(data, name=name)

            cover_field = self._cover_field(owner)
            if i == cover_index and cover_field:
                getattr(owner, cover_field).save(name, content, save=True)
            else:
                kwargs = {gallery_field: owner, "order": i}
                item = gallery_model(**kwargs)
                item.image.save(name, content, save=False)
                item.save()

        saved = total_before - total_after
        summary = (f"\n{total_before/1024/1024:.1f} MB of originals -> "
                   f"{total_after/1024/1024:.1f} MB uploaded. EXIF removed.")
        if saved > 0:
            summary += f" {saved/max(total_before,1)*100:.0f}% smaller."
        self.stdout.write(self.style.SUCCESS(summary))

        if bigger:
            self.stdout.write(self.style.WARNING(
                f"\n{len(bigger)} file(s) came out LARGER than the original: "
                f"{', '.join(bigger)}.\n"
                "That means they were already compressed and re-encoding cost "
                "quality for nothing. Upload those through the admin instead, or "
                "re-run with a smaller --max-width."))

        if not options["dry_run"]:
            self.stdout.write(
                "\nOpen each image in the admin and write its alt text. A photo "
                "with no description is invisible to a screen reader and to "
                "search engines.")

    # ------------------------------------------------------------------
    @staticmethod
    def _cover_field(owner):
        """
        Name of the field on this model that actually holds an uploaded file.

        Package and Destination carry BOTH an `image` URLField, for pointing at
        a photo hosted elsewhere, and an `image_upload` ImageField for a real
        file. `hasattr(owner, "image")` was true for all of them, so the command
        went for the URLField and called .save() on a plain string:

            AttributeError: 'str' object has no attribute 'save'

        Checking the field type rather than the attribute name picks the right
        one on every model, including any added later.
        """
        from django.db.models import FileField

        for candidate in ("image_upload", "image"):
            try:
                field = owner._meta.get_field(candidate)
            except Exception:
                continue
            if isinstance(field, FileField):
                return candidate
        return None

    # ------------------------------------------------------------------
    def _resolve(self, target, slug):
        from tours.models import (
            Accommodation, AccommodationImage, Destination, Package, PackageImage,
        )

        if target == "stay":
            owner = Accommodation.objects.filter(active=True).first()
            if owner is None:
                raise CommandError(
                    "No accommodation exists yet. Run: python manage.py seed_stay")
            return owner, AccommodationImage, "accommodation"

        if target == "package":
            owner = Package.objects.filter(slug=slug).first()
            if owner is None:
                raise CommandError(f"No package with slug {slug!r}")
            return owner, PackageImage, "package"

        owner = Destination.objects.filter(slug=slug).first()
        if owner is None:
            raise CommandError(f"No destination with slug {slug!r}")
        return owner, None, None

    def _prepare(self, path, max_width):
        """Open, rotate upright, resize, and re-encode without any metadata."""
        with Image.open(path) as im:
            # Phones record orientation in EXIF rather than rotating the pixels.
            im = ImageOps.exif_transpose(im)

            if im.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                converted = im.convert("RGBA")
                background.paste(converted, mask=converted.split()[-1])
                im = background
            elif im.mode != "RGB":
                im = im.convert("RGB")

            if im.width > max_width:
                height = round(im.height * max_width / im.width)
                im = im.resize((max_width, height), Image.LANCZOS)

            # A fresh image object carries no EXIF, so GPS and device data go.
            clean = Image.new("RGB", im.size)
            clean.putdata(list(im.getdata()))

            buffer = io.BytesIO()
            clean.save(buffer, format="JPEG", quality=QUALITY,
                       optimize=True, progressive=True)
            return buffer.getvalue(), clean.size
