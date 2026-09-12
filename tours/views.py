from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Min, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .data.tanzania_map import OUTLINES, VIEWBOX
from .data import kilimanjaro_map as kili
from .models import (
    Accommodation, Category, Destination, FAQ, HeroSlide, MapRoute, Package,
    RouteStop, TeamMember, TransferService, Testimonial,
)


def _published():
    return Package.objects.filter(published=True)


def home(request):
    # The tour cards read package.primary_category for the bead colour and the
    # label, so select_related keeps six cards at one query instead of seven.
    cards = _published().select_related("primary_category")

    context = {
        "slides": HeroSlide.objects.filter(active=True),
        # annotate rather than calling Category.package_count() in the template:
        # the tile grid was one COUNT query per category.
        "categories": (
            Category.objects.filter(featured=True)
            .annotate(package_count=Count("packages", distinct=True))
        ),
        "featured_packages": cards.filter(featured=True)[:6],
        "day_trips": cards.filter(duration_days=1)[:6],
        "destinations": Destination.objects.filter(featured=True)[:8],
        "transfers": TransferService.objects.filter(active=True),
        # The guest house is one of the things the client most wanted visible,
        # and it was reachable only from the top nav.
        "stay": Accommodation.objects.filter(active=True).first(),
        "testimonials": Testimonial.objects.filter(featured=True)[:6],
        "map_routes": (
            MapRoute.objects.filter(active=True)
            .select_related("package")
            .prefetch_related(
                Prefetch("stops", queryset=RouteStop.objects.select_related("destination"))
            )
        ),
        "total_packages": _published().count(),
        "map_outlines": OUTLINES,
        "map_viewbox": VIEWBOX,
    }
    return render(request, "tours/home.html", context)


def package_list(request):
    packages = _published().select_related("primary_category")

    category = request.GET.get("category")
    destination = request.GET.get("destination")
    query = request.GET.get("q", "").strip()
    max_days = request.GET.get("max_days")

    if category:
        packages = packages.filter(categories__slug=category)
    if destination:
        packages = packages.filter(destinations__slug=destination)
    if max_days:
        try:
            packages = packages.filter(duration_days__lte=int(max_days))
        except ValueError:
            pass
    if query:
        packages = packages.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(destinations__name__icontains=query)
        )

    packages = packages.distinct()
    page = Paginator(packages, 12).get_page(request.GET.get("page"))

    context = {
        "packages": page,
        "page_obj": page,
        "categories": Category.objects.all(),
        "destinations": Destination.objects.filter(featured=True),
        "active_category": category,
        "active_destination": destination,
        "query": query,
        # the paginator has already counted; asking the queryset again was a
        # second COUNT over the same filtered set.
        "total": page.paginator.count,
    }
    return render(request, "tours/package_list.html", context)


def package_index(request):
    """
    Every tour on one page, grouped by category.

    The paginated listing is for browsing; this is for finding. With 174 tours
    across 15 pages, checking whether a particular trip is on the site meant
    clicking Next fourteen times. Here everything is in the DOM at once, so the
    search box filters instantly and Ctrl+F works on the whole catalogue.
    """
    packages = (
        _published()
        .select_related("primary_category")
        .prefetch_related("destinations")
        .order_by("primary_category__order", "duration_days", "title")
    )

    groups = []
    for category in Category.objects.all():
        rows = [p for p in packages if p.primary_category_id == category.id]
        if rows:
            groups.append((category, rows))

    return render(request, "tours/package_index.html", {
        "groups": groups,
        "total": len(packages),
    })


def package_detail(request, slug):
    package = get_object_or_404(
        _published().prefetch_related("itinerary_days", "gallery", "destinations",
                                      "categories"),
        slug=slug,
    )
    related = (
        _published()
        .select_related("primary_category")
        .filter(categories__in=package.categories.all())
        .exclude(pk=package.pk)
        .distinct()[:3]
    )
    context = {"package": package, "related": related}
    if package.climb_route_id:
        context.update(_kilimanjaro_map_context())
    return render(request, "tours/package_detail.html", context)


def _kilimanjaro_map_context():
    """
    Geometry for the plan-view climb map.

    Projected here rather than in the template because Django templates cannot
    do arithmetic, and rather than in the model because none of it depends on
    which route is being drawn — it is the same mountain every time.
    """
    contours = []
    for i, c in enumerate(kili.CONTOURS):
        ring = dict(zip(("cx", "cy", "rx", "ry"), _ellipse(*c)))
        # Opacity is computed here and written onto the element as a plain
        # attribute. It used to be a CSS `calc()` over a custom property, and
        # where that failed to parse the opacity fell back to 1 — so all seven
        # rings painted at full strength on top of each other and the map came
        # out as a solid black blob. A number in the markup cannot fail that way.
        ring["opacity"] = round(0.045 + i * 0.022, 3)
        contours.append(ring)

    mawenzi = dict(zip(("cx", "cy", "rx", "ry"), _ellipse(*kili.MAWENZI)))
    mawenzi["opacity"] = 0.10
    shira = dict(zip(("cx", "cy", "rx", "ry"), _ellipse(*kili.SHIRA_PLATEAU)))
    shira["opacity"] = 0.10

    return {
        "map_viewbox": kili.VIEWBOX,
        "map_contours": contours,
        "map_mawenzi": mawenzi,
        "map_shira": shira,
        "map_landmarks": [
            {"name": name, "x": kili.project(lon, lat)[0], "y": kili.project(lon, lat)[1]}
            for name, lon, lat in kili.LANDMARKS
        ],
    }


def _ellipse(lon, lat, r_lon, r_lat):
    """Centre plus radii in degrees -> centre plus radii in SVG units."""
    cx, cy = kili.project(lon, lat)
    edge_x, _ = kili.project(lon + r_lon, lat)
    _, edge_y = kili.project(lon, lat + r_lat)
    return cx, cy, round(abs(edge_x - cx), 1), round(abs(edge_y - cy), 1)


def category_list(request):
    categories = Category.objects.all()
    return render(request, "tours/category_list.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    packages = (
        _published().filter(categories=category)
        .select_related("primary_category").distinct()
    )
    page = Paginator(packages, 12).get_page(request.GET.get("page"))
    return render(request, "tours/category_detail.html", {
        "category": category,
        "packages": page,
        "page_obj": page,
        "total": page.paginator.count,
    })


def destination_list(request):
    destinations = (
        Destination.objects.all()
        .annotate(from_price=Min("packages__price_from"))
    )
    return render(request, "tours/destination_list.html",
                  {"destinations": destinations})


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    packages = (
        _published().filter(destinations=destination)
        .select_related("primary_category").distinct()
    )
    return render(request, "tours/destination_detail.html",
                  {"destination": destination, "packages": packages})


def day_trip_list(request):
    packages = _published().filter(duration_days=1).select_related("primary_category")
    return render(request, "tours/day_trip_list.html", {"packages": packages})


def transfers(request):
    return render(request, "tours/transfers.html", {
        "transfers": TransferService.objects.filter(active=True),
        "stay": Accommodation.objects.filter(active=True).first(),
    })


def stay(request):
    """The operator's own guest house."""
    accommodation = (
        Accommodation.objects.filter(active=True)
        .prefetch_related("features", "gallery")
        .first()
    )
    return render(request, "tours/stay.html", {
        "stay": accommodation,
        "transfers": TransferService.objects.filter(active=True),
    })


def about(request):
    return render(request, "tours/about.html", {
        "team": TeamMember.objects.filter(active=True),
    })


def faq(request):
    return render(request, "tours/faq.html", {"faqs": FAQ.objects.all()})


def reviews(request):
    return render(request, "tours/reviews.html", {
        "testimonials": Testimonial.objects.all(),
    })


def contact(request):
    initial = {}
    if request.GET.get("stay"):
        initial["package_interest"] = "Accommodation"
    package_slug = request.GET.get("package")
    package = None
    if package_slug:
        package = Package.objects.filter(slug=package_slug).first()
        if package:
            initial["package"] = package.pk
            initial["package_interest"] = package.title

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you — your enquiry has been received. Our team will be in touch shortly.",
            )
            return redirect("tours:contact")
    else:
        form = ContactForm(initial=initial)

    return render(request, "tours/contact.html", {"form": form, "package": package})


def privacy_policy(request):
    return render(request, "tours/privacy_policy.html")


def terms(request):
    return render(request, "tours/terms.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {settings.SITE_DOMAIN}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
