from django.db import models
from django.urls import reverse

from .validators import validate_image, validate_video


class Category(models.Model):
    """A top-level tour category, e.g. 'Safari / Wildlife Tours'."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    code = models.CharField(max_length=40, blank=True, help_text="Short key, e.g. SAFARI")
    short_description = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="categories/", blank=True, null=True, validators=[validate_image])
    video = models.FileField(
        upload_to="categories/video/", blank=True, null=True, validators=[validate_video])

    bead_colour = models.CharField(
        max_length=7, default="#B98431",
        help_text="Hex colour of this category's bead in the navigation menu.")

    order = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=True, help_text="Show in the main navigation")

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tours:category_detail", kwargs={"slug": self.slug})

    def package_count(self):
        return self.packages.count()


class Destination(models.Model):
    """A park, town, island or region. One row per real place."""
    REGION_CHOICES = [
        ("northern", "Northern Circuit"),
        ("southern", "Southern Circuit"),
        ("western", "Western Tanzania"),
        ("coastal", "Coast & Islands"),
        ("zanzibar", "Zanzibar"),
        ("mountain", "Mountains & Highlands"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default="other")

    aliases = models.TextField(
        blank=True,
        help_text="Other spellings the client uses, one per line. Used when importing "
                  "content so 'Serengeti' and 'Serengeti National Park' stay one place.",
    )

    latitude = models.FloatField(
        blank=True, null=True,
        help_text="Decimal degrees, negative south of the equator. Used to place "
                  "this destination on the routes map.")
    longitude = models.FloatField(blank=True, null=True, help_text="Decimal degrees.")

    short_description = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)

    image = models.URLField(blank=True, help_text="Image URL, or upload a file below")
    image_upload = models.ImageField(
        upload_to="destinations/", blank=True, null=True, validators=[validate_image])
    video = models.FileField(
        upload_to="destinations/video/", blank=True, null=True, validators=[validate_video],
        help_text="Optional background clip (mp4/webm), muted and short.")

    order = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_image(self):
        return self.image_upload.url if self.image_upload else self.image

    def get_absolute_url(self):
        return reverse("tours:destination_detail", kwargs={"slug": self.slug})

    def alias_list(self):
        return [a.strip() for a in self.aliases.splitlines() if a.strip()]

    def map_point(self):
        """SVG coordinates for the routes map, or None if not geocoded."""
        if self.latitude is None or self.longitude is None:
            return None
        from .data.tanzania_map import project
        return project(self.longitude, self.latitude)


class Package(models.Model):
    """
    A bookable tour. Covers day trips and multi-day journeys alike — a day trip
    is simply a package with duration_days = 1.
    """
    PRICE_BASIS_CHOICES = [
        ("person", "per person"),
        ("couple", "per couple"),
        ("adult", "per adult"),
        ("group", "per group"),
        ("boat", "per private boat"),
        ("vehicle", "per vehicle"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)

    # A tour can legitimately sit in several categories — Usambara appears as
    # trekking, nature AND camping. M2M keeps one page per tour instead of
    # three near-identical pages competing with each other in search.
    categories = models.ManyToManyField(Category, related_name="packages")
    primary_category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="primary_packages",
        help_text="Used for the breadcrumb and the canonical URL.")

    # --- Duration ---------------------------------------------------------
    duration_days = models.PositiveIntegerField(
        blank=True, null=True, help_text="Leave blank for activities priced by the hour.")
    duration_nights = models.PositiveIntegerField(blank=True, null=True)
    duration_text = models.CharField(
        max_length=60, blank=True,
        help_text="Shown when there is no whole-day figure, e.g. '2–3 hours', 'Half day'.")

    starting_point = models.CharField(max_length=200, blank=True)
    destinations = models.ManyToManyField(Destination, blank=True, related_name="packages")
    route = models.CharField(
        max_length=120, blank=True, help_text="Climbing route, e.g. 'Machame Route'")

    # --- Price ------------------------------------------------------------
    price_from = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=8, default="USD")
    price_basis = models.CharField(
        max_length=12, choices=PRICE_BASIS_CHOICES, default="person",
        help_text="A couple package priced per couple must NOT display as per person.")

    # --- Copy -------------------------------------------------------------
    short_description = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True, help_text="One per line")
    includes = models.TextField(blank=True, help_text="One per line")
    excludes = models.TextField(blank=True, help_text="One per line")
    best_for = models.TextField(blank=True)
    important_note = models.TextField(
        blank=True, help_text="Caveats — wildlife sightings, weather, permits.")

    # --- Media ------------------------------------------------------------
    image = models.URLField(blank=True)
    image_upload = models.ImageField(
        upload_to="packages/", blank=True, null=True, validators=[validate_image])
    video = models.FileField(
        upload_to="packages/video/", blank=True, null=True, validators=[validate_video])

    featured = models.BooleanField(default=False)
    published = models.BooleanField(
        default=True, help_text="Untick to hide a package that is missing content.")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "duration_days", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tours:package_detail", kwargs={"slug": self.slug})

    def get_image(self):
        return self.image_upload.url if self.image_upload else self.image

    # --- Display helpers --------------------------------------------------
    def duration_display(self):
        if self.duration_days:
            nights = self.duration_nights
            if nights is None:
                nights = max(self.duration_days - 1, 0)
            if self.duration_days == 1:
                return "1 day"
            return f"{self.duration_days} days / {nights} nights"
        return self.duration_text or ""

    def price_display(self):
        if self.price_from is None:
            return "On request"
        amount = f"{self.price_from:,.0f}"
        return f"From {self.currency} {amount} {self.get_price_basis_display()}"

    def is_day_trip(self):
        return self.duration_days == 1

    def highlight_list(self):
        return [h.strip() for h in self.highlights.splitlines() if h.strip()]

    def include_list(self):
        return [h.strip() for h in self.includes.splitlines() if h.strip()]

    def exclude_list(self):
        return [h.strip() for h in self.excludes.splitlines() if h.strip()]

    def is_complete(self):
        """Used by the admin to flag packages that are not ready to sell."""
        return bool(self.includes and self.excludes and self.short_description)


class ItineraryDay(models.Model):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="itinerary_days")
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["day_number"]
        unique_together = [("package", "day_number")]

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


class PackageImage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(
        upload_to="packages/gallery/", validators=[validate_image])
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.package.title} — image {self.pk}"


class HeroSlide(models.Model):
    """A slide in the homepage hero carousel — still image or looping video."""
    eyebrow = models.CharField(max_length=120, blank=True)
    headline = models.CharField(max_length=160)
    headline_script = models.CharField(
        max_length=80, blank=True,
        help_text="Short second line set in the script face, e.g. 'up close'")
    subline = models.CharField(max_length=250, blank=True)

    image = models.ImageField(
        upload_to="hero/", blank=True, null=True, validators=[validate_image],
        help_text="Still background; also the poster frame for the video.")
    video = models.FileField(
        upload_to="hero/video/", blank=True, null=True, validators=[validate_video],
        help_text="Muted looping clip. The image is used instead on mobile.")

    cta_label = models.CharField(max_length=60, blank=True)
    cta_url = models.CharField(max_length=300, blank=True)

    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.headline

    def has_video(self):
        return bool(self.video)
    has_video.boolean = True


class TransferService(models.Model):
    """Airport transfers, hotel pickups, city tours — the transport side."""
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=40, blank=True, help_text="Lucide icon name, e.g. 'plane'")
    image = models.ImageField(
        upload_to="transfers/", blank=True, null=True, validators=[validate_image])
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    author_name = models.CharField(max_length=120)
    author_country = models.CharField(max_length=100, blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    package = models.ForeignKey(
        Package, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="testimonials")
    featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name} ({self.rating}/5)"


class TeamMember(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to="team/", blank=True, null=True, validators=[validate_image])
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class FAQ(models.Model):
    question = models.CharField(max_length=250)
    answer = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="faqs")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    package = models.ForeignKey(
        Package, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="enquiries")
    package_interest = models.CharField(max_length=200, blank=True)
    travel_date = models.DateField(blank=True, null=True)
    adults = models.PositiveSmallIntegerField(blank=True, null=True)
    children = models.PositiveSmallIntegerField(blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.created_at:%Y-%m-%d}"


class MapRoute(models.Model):
    """
    One coloured line on the homepage routes map.

    A route is a named journey shape — "Northern circuit", "Bush to beach" —
    drawn through an ordered list of destinations. It usually mirrors a real
    package, but it is kept separate: the map wants a handful of clean lines,
    not all 174 tours drawn on top of each other.
    """
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    colour = models.CharField(
        max_length=7, default="#B98431",
        help_text="Hex colour for the line and its legend swatch, e.g. #B98431")
    summary = models.CharField(max_length=200, blank=True)
    package = models.ForeignKey(
        Package, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="map_routes",
        help_text="Optional — links the legend entry through to a bookable tour.")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def points(self):
        """Projected SVG points for every stop that has coordinates."""
        out = []
        for stop in self.stops.select_related("destination"):
            point = stop.destination.map_point()
            if point:
                out.append((stop.destination, point))
        return out

    def _offset_points(self):
        """
        Nudge each route a little to one side of the straight line between
        stops. Several routes share the same legs — Arusha to Serengeti is on
        three of them — and without this the lines sit exactly on top of one
        another and only the last one drawn is visible.
        """
        pts = [p for _d, p in self.points()]
        if len(pts) < 2:
            return pts
        # alternate sides, widening slightly for each successive route
        step = (self.order + 1) // 2
        side = 1 if self.order % 2 == 0 else -1
        shift = side * step * 5.0
        if shift == 0:
            return pts

        out = []
        for i, (x, y) in enumerate(pts):
            # direction of travel at this point, to find the perpendicular
            ax, ay = pts[max(i - 1, 0)]
            bx, by = pts[min(i + 1, len(pts) - 1)]
            dx, dy = bx - ax, by - ay
            length = (dx * dx + dy * dy) ** 0.5 or 1.0
            out.append((x + (-dy / length) * shift, y + (dx / length) * shift))
        return out

    def path_d(self):
        """
        An SVG path through the stops as a smooth curve rather than straight
        legs. Uses Catmull-Rom control points converted to cubic beziers, which
        passes exactly through every stop while rounding the corners.
        """
        pts = self._offset_points()
        if len(pts) < 2:
            return ""
        if len(pts) == 2:
            (x1, y1), (x2, y2) = pts
            return f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"

        d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1, p2 = pts[i], pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else p2
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d.append(
                f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
                f"{p2[0]:.1f},{p2[1]:.1f}"
            )
        return " ".join(d)

    def path_length(self):
        """
        Approximate pixel length, used for stroke-dasharray so the draw-on
        animation covers the whole line. Rounded up generously — a dasharray
        shorter than the real path leaves a visible gap.
        """
        pts = self._offset_points()
        total = 0.0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return round(total * 1.15) or 1

    def marker_points(self):
        """Offset positions for the stop markers, so they sit on the curve."""
        return [
            (dest, point)
            for (dest, _orig), point in zip(self.points(), self._offset_points())
        ]


class RouteStop(models.Model):
    route = models.ForeignKey(MapRoute, on_delete=models.CASCADE, related_name="stops")
    destination = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name="route_stops")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = [("route", "destination", "order")]

    def __str__(self):
        return f"{self.route.name} — {self.order}. {self.destination.name}"
