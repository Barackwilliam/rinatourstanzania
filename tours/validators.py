"""Upload guards for the media that goes into the Supabase bucket."""

from django.conf import settings
from django.core.exceptions import ValidationError


IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "avif"}
VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "m4v"}


def _extension(f):
    return f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""


def _check(f, allowed, max_mb, label):
    ext = _extension(f)
    if ext not in allowed:
        raise ValidationError(
            f"{label} must be one of: {', '.join(sorted(allowed))}. Got '.{ext}'."
        )
    if f.size > max_mb * 1024 * 1024:
        raise ValidationError(
            f"{label} is {f.size / 1024 / 1024:.1f} MB — the limit is {max_mb} MB. "
            "Compress it before uploading."
        )


def validate_image(f):
    _check(f, IMAGE_EXTENSIONS, settings.MAX_IMAGE_UPLOAD_MB, "Image")


def validate_video(f):
    _check(f, VIDEO_EXTENSIONS, settings.MAX_VIDEO_UPLOAD_MB, "Video")
