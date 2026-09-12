from collections import OrderedDict

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Min

from .models import Category, Destination, Package

_KEYS = [
    "SITE_NAME", "SITE_TAGLINE",
    "SITE_PHONE_PRIMARY", "SITE_PHONE_SECONDARY", "SITE_WHATSAPP", "SITE_WHATSAPP_DISPLAY",
    "SITE_EMAIL", "SITE_EMAIL_SECONDARY", "SITE_LOCATION",
    "SITE_INSTAGRAM", "SITE_FACEBOOK", "SITE_TIKTOK", "SITE_THREADS",
    "SITE_DOMAIN", "SITE_MAP_EMBED_URL",
    "GOOGLE_ANALYTICS_ID", "GOOGLE_SITE_VERIFICATION",
]

# Cleared by tours.signals whenever a model the menus read from is saved, so an
# admin edit shows up on the next page load instead of waiting out the TTL.
NAV_CACHE_KEY = "tours:navigation:v1"


def site_settings(request):
    ctx = {key: getattr(settings, key, "") for key in _KEYS}
    ctx["request_path"] = request.path
    return ctx


def _build_navigation():
    """
    Everything the two dropdown menus need, on every page.

    Destinations are grouped by region rather than listed flat: 55 places in one
    column is a wall, the same 55 under six headings is a map of the country.
    Both queries are annotated so the menu can show tour counts without a query
    per row.

    Querysets are forced to lists here rather than left lazy: the whole dict
    goes into the cache, and a lazy queryset would just re-run on every page
    that read it back.
    """
    categories = list(
        Category.objects.filter(featured=True)
        .annotate(n_tours=Count("packages", distinct=True))
    )

    destinations = list(
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
    # Reuses the list above instead of firing a seventh query.
    footer_images = [url for url in (d.get_image() for d in destinations) if url][:6]

    return {
        "footer_images": footer_images,
        "nav_promoted": promoted,
        "nav_categories": categories,
        "nav_destinations": destinations[:10],
        "nav_destination_groups": grouped,
        # len() on the list we already hold, not another COUNT round trip.
        "nav_destination_total": len(destinations),
    }


def navigation(request):
    """
    The header and footer are identical on every page, so their six queries were
    being paid on every page — including pages that then only need two of their
    own. Built once and cached; tours.signals clears the entry the moment
    anything the menus read from changes in the admin.
    """
    ttl = getattr(settings, "NAV_CACHE_SECONDS", 600)
    if not ttl:
        return _build_navigation()

    data = cache.get(NAV_CACHE_KEY)
    if data is None:
        data = _build_navigation()
        cache.set(NAV_CACHE_KEY, data, ttl)
    return data
