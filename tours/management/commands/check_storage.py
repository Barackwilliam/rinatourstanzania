"""
Upload a tiny file to the configured media storage and print its public URL.

    python manage.py check_storage

Run this once after filling in the Supabase env vars — it confirms the bucket,
the S3 keys and the public URL shape all work, before you upload a 90 MB video
and find out the hard way.
"""

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Verify that media uploads reach the configured storage backend."

    def handle(self, *args, **options):
        backend = settings.STORAGES["default"]["BACKEND"]
        self.stdout.write(f"Backend: {backend}")

        if not settings.SUPABASE_PROJECT_REF:
            self.stdout.write(self.style.WARNING(
                "SUPABASE_PROJECT_REF is empty — using the local filesystem. "
                "Fill it in .env to test the bucket."
            ))
        else:
            self.stdout.write(f"Bucket:  {settings.SUPABASE_STORAGE_BUCKET}")
            self.stdout.write(f"Region:  {settings.SUPABASE_S3_REGION}")

        name = None
        try:
            name = default_storage.save(
                "_healthcheck/ping.txt", ContentFile(b"ok")
            )
            url = default_storage.url(name)
            self.stdout.write(self.style.SUCCESS("Upload OK"))
            self.stdout.write(f"URL: {url}")
            self.stdout.write(
                "Open that URL in a browser. If it 400s, the bucket is not public "
                "(Supabase > Storage > bucket > Settings > Public bucket)."
            )
        except Exception as exc:
            raise SystemExit(
                self.style.ERROR(f"Upload FAILED: {type(exc).__name__}: {exc}")
            )
        finally:
            if name and default_storage.exists(name):
                default_storage.delete(name)
                self.stdout.write("Test file deleted.")
