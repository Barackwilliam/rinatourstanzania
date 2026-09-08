"""
Django settings — Rina Tours Tanzania (JamiiTek Digital Agency).

Every secret and every piece of client-specific branding is read from the
environment. Nothing is hardcoded here, so this file can ship as-is to any
client project: copy .env.example to .env, fill it in, done.

Media (images + video) is stored in a Supabase Storage bucket, NOT on the
Render disk — Render's filesystem is wiped on every deploy.
"""

# database : <email that owns the Supabase project — fill this in>
# hosting  : <email that owns the Render account — fill this in>

from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core security -----------------------------------------------------------
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

RENDER_EXTERNAL_HOSTNAME = config("RENDER_EXTERNAL_HOSTNAME", default="")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# --- Applications ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "storages",
    "tours",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tours.context_processors.site_settings",
                "tours.context_processors.navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ------------------------------------------------------------------
# Supabase: Project Settings > Database > Connection string (URI).
# Use the SESSION POOLER uri on Render's free tier.
# Falls back to SQLite locally when DATABASE_URL is unset.
_database_url = config("DATABASE_URL", default="")
if _database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            ssl_require=config("DB_SSL_REQUIRE", default=True, cast=bool),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Password validation -------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization -------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Dar_es_Salaam"
USE_I18N = True
USE_TZ = True

# --- Static files (served by WhiteNoise from the Render disk) ---------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# --- Media: images + video in a Supabase Storage bucket ---------------------------
# Supabase dashboard:
#   1. Storage > New bucket > name it (e.g. "media"), tick PUBLIC
#   2. Storage > S3 Access Keys > New access key  -> gives you an ID + secret
#   3. Project Settings > General > Reference ID  -> that's SUPABASE_PROJECT_REF
#
# Leave SUPABASE_PROJECT_REF empty locally and uploads land in ./media/ instead,
# so you can develop without touching the bucket.
SUPABASE_PROJECT_REF = config("SUPABASE_PROJECT_REF", default="")
SUPABASE_STORAGE_BUCKET = config("SUPABASE_STORAGE_BUCKET", default="media")
SUPABASE_S3_REGION = config("SUPABASE_S3_REGION", default="eu-central-1")

if SUPABASE_PROJECT_REF:
    AWS_ACCESS_KEY_ID = config("SUPABASE_S3_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("SUPABASE_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = SUPABASE_STORAGE_BUCKET
    AWS_S3_REGION_NAME = SUPABASE_S3_REGION
    AWS_S3_ENDPOINT_URL = f"https://{SUPABASE_PROJECT_REF}.storage.supabase.co/storage/v1/s3"

    # Public read URLs come straight off the CDN, not signed & not expiring.
    AWS_S3_CUSTOM_DOMAIN = (
        f"{SUPABASE_PROJECT_REF}.supabase.co"
        f"/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}"
    )
    AWS_QUERYSTRING_AUTH = False

    # Supabase speaks S3 but not ACLs, and only path-style addressing.
    AWS_DEFAULT_ACL = None
    AWS_S3_ADDRESSING_STYLE = "path"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_FILE_OVERWRITE = False

    # Browsers cache media for a year; filenames are unique so this is safe.
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000, public"}

    _default_storage = {"BACKEND": "storages.backends.s3.S3Storage"}
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
else:
    _default_storage = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": _default_storage,
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Upload ceilings — a 4K hero video will blow past the default 2.5 MB.
DATA_UPLOAD_MAX_MEMORY_SIZE = config("MAX_UPLOAD_MB", default=100, cast=int) * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # spill to a temp file past 5 MB

MAX_IMAGE_UPLOAD_MB = config("MAX_IMAGE_UPLOAD_MB", default=8, cast=int)
MAX_VIDEO_UPLOAD_MB = config("MAX_VIDEO_UPLOAD_MB", default=100, cast=int)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Production hardening --------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = "DENY"

# --- Client branding (all from .env — nothing client-specific in this file) --------
SITE_NAME = config("SITE_NAME", default="Tour Company")
SITE_TAGLINE = config("SITE_TAGLINE", default="")
SITE_PHONE_PRIMARY = config("SITE_PHONE_PRIMARY", default="")
SITE_PHONE_SECONDARY = config("SITE_PHONE_SECONDARY", default="")
SITE_WHATSAPP = config("SITE_WHATSAPP", default="")
SITE_EMAIL = config("SITE_EMAIL", default="")
SITE_LOCATION = config("SITE_LOCATION", default="")
SITE_INSTAGRAM = config("SITE_INSTAGRAM", default="")
SITE_FACEBOOK = config("SITE_FACEBOOK", default="")
SITE_TIKTOK = config("SITE_TIKTOK", default="")
SITE_THREADS = config("SITE_THREADS", default="")

SITE_DOMAIN = config("SITE_DOMAIN", default="http://127.0.0.1:8000")
SITE_MAP_EMBED_URL = config("SITE_MAP_EMBED_URL", default="")
GOOGLE_ANALYTICS_ID = config("GOOGLE_ANALYTICS_ID", default="")
GOOGLE_SITE_VERIFICATION = config("GOOGLE_SITE_VERIFICATION", default="")
