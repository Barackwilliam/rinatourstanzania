from collections import OrderedDict

from django.conf import settings
from django.db.models import Count, Min

from .models import Category, Destination, Package

_KEYS = [
    "SITE_NAME", "SITE_TAGLINE",
    "SITE_PHONE_PRIMARY", "SITE_PHONE_SECONDARY", "SITE_WHATSAPP",
    "SITE_EMAIL", "SITE_LOCATION",
    "SITE_INSTAGRAM", "SITE_FACEBOOK", "SITE_TIKTOK", "SITE_THREADS",
    "SITE_DOMAIN", "SITE_MAP_EMBED_URL",
    "GOOGLE_ANALYTICS_ID", "GOOGLE_SITE_VERIFICATION",
]


def site_settings(request):
    ctx = {key: getattr(settings, key, "") for key in _KEYS}
    ctx["request_path"] = request.path
    return ctx


def navigation(request):
    """
    Everything the two dropdown menus need, on every page.

    Destinations are grouped by region rather than listed flat: 55 places in one
    column is a wall, the same 55 under six headings is a map of the country.
    Both queries are annotated so the menu can show tour counts without a query
    per row.
    """
    categories = (
        Category.objects.filter(featured=True)
        .annotate(n_tours=Count("packages", distinct=True))
    )

    destinations = (
        Destination.objects.filter(featured=True)
        .annotate(
            n_tours=Count("packages", distinct=True),
            from_price=Min("packages__price_from"),
        )
        .filter(n_tours__gt=0)
    )

    # Ordered so the menu reads north to south, then out to the islands.
    region_order = ["northern", "mountain", "southern", "western", "coastal", "zanzibar"]
    labels = dict(Destination.REGION_CHOICES)

    grouped = OrderedDict()
    for key in region_order:
        places = [d for d in destinations if d.region == key]
        if places:
            grouped[labels.get(key, key)] = places[:7]

    # One promoted tour in each menu. Prefer something flagged featured and
    # actually finished; fall back to the most expensive published tour so the
    # panel is never empty.
    promoted = (
        Package.objects.filter(published=True, featured=True)
        .select_related("primary_category").first()
        or Package.objects.filter(published=True)
        .select_related("primary_category")
        .order_by("-price_from").first()
    )

    # Photographs for the slow crossfade behind the footer. Whatever imagery the
    # client has uploaded gets reused here rather than asking for more; if there
    # is none the layer is skipped entirely and the footer stays flat green.
    footer_images = [
        d.get_image() for d in
        Destination.objects.filter(featured=True).exclude(
            image_upload="", image="")[:6]
        if d.get_image()
    ]

    return {
        "footer_images": footer_images,
        "nav_promoted": promoted,
        "nav_categories": categories,
        "nav_destinations": destinations[:10],
        "nav_destination_groups": grouped,
        "nav_destination_total": destinations.count(),
    }
