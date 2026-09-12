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
        max_length=7, default="#B5813F",
        help_text="Hex colour marking this category in the menu and on cards.")

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
    climb_route = models.ForeignKey(
        "ClimbRoute", on_delete=models.SET_NULL, blank=True, null=True,
        related_name="packages",
        help_text="Draws the altitude profile on this tour's page.")

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
        indexes = [
            # Every listing page starts from published=True, and the homepage
            # and day-trip page narrow it further. Without these Postgres scans
            # the whole table on each one.
            models.Index(fields=["published", "featured"], name="pkg_pub_feat_idx"),
            models.Index(fields=["published", "duration_days"], name="pkg_pub_days_idx"),
            models.Index(fields=["order", "duration_days", "title"], name="pkg_order_idx"),
        ]

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
    """
    Airport transfers, town runs and day hire.

    Priced per trip or per day rather than per person — a taxi to Arusha costs
    the same whether one person or three are in it, and showing a per-person
    figure would misprice it.
    """
    BASIS_CHOICES = [
        ("trip", "per trip"),
        ("day", "per day"),
        ("person", "per person"),
        ("cup", "per cup"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)

    route_from = models.CharField(max_length=120, blank=True)
    route_to = models.CharField(max_length=120, blank=True)
    distance_km = models.PositiveIntegerField(blank=True, null=True)
    duration_text = models.CharField(
        max_length=60, blank=True, help_text="e.g. '9-15 minutes'")

    price_from = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    price_to = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        help_text="Fill in only when the price is a range.")
    currency = models.CharField(max_length=8, default="USD")
    price_basis = models.CharField(max_length=10, choices=BASIS_CHOICES, default="trip")

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

    def price_display(self):
        if self.price_from is None:
            return "On request"
        basis = self.get_price_basis_display()
        if self.price_to and self.price_to != self.price_from:
            return f"{self.currency} {self.price_from:,.0f}-{self.price_to:,.0f} {basis}"
        return f"{self.currency} {self.price_from:,.0f} {basis}"

    def route_display(self):
        if self.route_from and self.route_to:
            return f"{self.route_from} to {self.route_to}"
        return self.route_to or self.route_from or ""


class Accommodation(models.Model):
    """
    Where guests stay. The operator runs their own place, so this is a room
    rate rather than a tour: priced per person per night, and the board basis
    matters because self-catering is allowed.
    """
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    location = models.CharField(max_length=160, blank=True)
    price_from = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=8, default="USD")
    board_basis = models.CharField(
        max_length=60, blank=True,
        help_text="e.g. 'Bed & breakfast'. Shown next to the rate.")

    image = models.ImageField(
        upload_to="stay/", blank=True, null=True, validators=[validate_image])
    video = models.FileField(
        upload_to="stay/video/", blank=True, null=True, validators=[validate_video])

    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "accommodation"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tours:stay")

    def price_display(self):
        if self.price_from is None:
            return "On request"
        rate = f"From {self.currency} {self.price_from:,.0f} per person per night"
        return f"{rate}, {self.board_basis.lower()}" if self.board_basis else rate


class AccommodationFeature(models.Model):
    """One line of what the place offers — views, kitchen access, birdlife."""
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name="features")
    title = models.CharField(max_length=120)
    detail = models.CharField(max_length=250, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="stay/gallery/", validators=[validate_image])
    alt_text = models.CharField(
        max_length=200, blank=True,
        help_text="What the photo shows, for screen readers and search engines. "
                  "'Guests having coffee on the veranda', not 'IMG_4821'.")
    caption = models.CharField(
        max_length=200, blank=True, help_text="Shown under the photo. Optional.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.accommodation.name} — image {self.pk}"


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
        max_length=7, default="#B5813F",
        help_text="Hex colour for the line and its legend swatch, e.g. #C2662B")
    summary = models.CharField(max_length=200, blank=True)
    package = models.ForeignKey(
        Package, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="map_routes",
        help_text="Optional — links the legend entry through to a bookable tour.")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._points_cache = None
        self._offset_cache = None

    def __str__(self):
        return self.name

    def points(self):
        """
        Projected SVG points for every stop that has coordinates.

        `stops.all()` rather than `stops.select_related(...)`: the homepage
        prefetches `stops__destination`, and any queryset method on the related
        manager throws that prefetched cache away and re-queries. Six routes
        each asked for their stops three times per template call was 43 of the
        homepage's 71 queries.

        The result is memoised on the instance too — `path_d`, `path_length`
        and `marker_points` all want the same list, and `marker_points` is
        rendered twice (map markers, then the legend).
        """
        if self._points_cache is None:
            out = []
            for stop in self.stops.all():
                point = stop.destination.map_point()
                if point:
                    out.append((stop.destination, point))
            self._points_cache = out
        return self._points_cache

    def _offset_points(self):
        """
        Nudge each route a little to one side of the straight line between
        stops. Several routes share the same legs — Arusha to Serengeti is on
        three of them — and without this the lines sit exactly on top of one
        another and only the last one drawn is visible.
        """
        if self._offset_cache is not None:
            return self._offset_cache

        pts = [p for _d, p in self.points()]
        if len(pts) < 2:
            self._offset_cache = pts
            return pts
        # alternate sides, widening slightly for each successive route
        step = (self.order + 1) // 2
        side = 1 if self.order % 2 == 0 else -1
        shift = side * step * 5.0
        if shift == 0:
            self._offset_cache = pts
            return pts

        out = []
        for i, (x, y) in enumerate(pts):
            # direction of travel at this point, to find the perpendicular
            ax, ay = pts[max(i - 1, 0)]
            bx, by = pts[min(i + 1, len(pts) - 1)]
            dx, dy = bx - ax, by - ay
            length = (dx * dx + dy * dy) ** 0.5 or 1.0
            out.append((x + (-dy / length) * shift, y + (dx / length) * shift))
        self._offset_cache = out
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


class ClimbRoute(models.Model):
    """
    A named way up a mountain, with its camps and their altitudes.

    Kept separate from Package because several packages share one route — the
    six-day and seven-day Machame climbs walk the same path at different paces —
    and the profile should be edited once, not once per package.
    """
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    mountain = models.CharField(max_length=80, default="Mount Kilimanjaro")
    summary = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._map_cache = None

    def __str__(self):
        return f"{self.mountain} — {self.name}"

    def stage_list(self):
        return list(self.stages.all())

    def map_stages(self):
        """
        Camps that have a position, in walking order, with duplicates collapsed.

        Marangu and Rongai come back down through camps they already passed, so
        the raw stage list repeats Horombo and Marangu Gate. On a profile that
        repetition is the point — it shows the descent. On a plan view it would
        just draw the line back over itself, so the second visit is dropped and
        the marker keeps the day of the first.
        """
        if self._map_cache is None:
            seen, out = set(), []
            for stage in self.stage_list():
                point = stage.map_point()
                if point is None or stage.name in seen:
                    continue
                seen.add(stage.name)
                out.append({
                    "stage": stage,
                    "x": point[0],
                    "y": point[1],
                    "verified": stage.coords_verified,
                })
            self._map_cache = out
        return self._map_cache

    def has_map(self):
        """Two placed camps is the minimum that draws as a route."""
        return len(self.map_stages()) >= 2

    def map_unverified(self):
        """How many placed camps nobody has confirmed yet."""
        return sum(1 for s in self.map_stages() if not s["verified"])

    @staticmethod
    def _smooth_path(pts):
        """
        A smooth path through a list of points, same Catmull-Rom treatment as
        the country map so the two read as the same family of drawing.
        """
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
            d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
                     f"{p2[0]:.1f},{p2[1]:.1f}")
        return " ".join(d)

    def _summit_index(self):
        """Where the highest camp falls in the plotted list."""
        stages = self.map_stages()
        if not stages:
            return 0
        return max(range(len(stages)), key=lambda i: stages[i]["stage"].altitude_m)

    def map_path_d(self):
        """The climb up: gate to summit."""
        pts = [(s["x"], s["y"]) for s in self.map_stages()]
        return self._smooth_path(pts[:self._summit_index() + 1])

    def map_descent_d(self):
        """
        The way down, drawn separately.

        Rongai summits and then walks out over Marangu; Machame comes down to
        Mweka. Drawn as one line with the ascent, the descent crosses back over
        the climb and the whole thing reads as a mistake. Split and dashed, the
        crossing becomes the information: you do not come down the way you went
        up.
        """
        pts = [(s["x"], s["y"]) for s in self.map_stages()]
        return self._smooth_path(pts[self._summit_index():])

    def map_path_length(self):
        """Length of the ascent line, for the draw-on animation."""
        pts = [(s["x"], s["y"]) for s in self.map_stages()][:self._summit_index() + 1]
        total = 0.0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return round(total * 1.15) or 1

    def map_viewbox(self):
        """
        A viewBox cropped to this route rather than the whole mountain.

        The projection has to cover every route — Lemosho starts far west,
        Rongai far north — so on one fixed frame any single route sits small in
        the middle with a lot of empty contour around it. Cropping to the
        route's own extent lets each one fill its panel, and because the relief
        is drawn in the same coordinate space it simply crops with it, which
        reads as zooming into the mountain.

        Padded generously and held to the base aspect ratio so the ellipses
        stay round and short routes are not blown up past what the approximate
        positions can honestly support.
        """
        from .data.kilimanjaro_map import WIDTH, HEIGHT, VIEWBOX

        pts = [(s["x"], s["y"]) for s in self.map_stages()]
        if len(pts) < 2:
            return VIEWBOX

        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        pad = max((max_x - min_x), (max_y - min_y)) * 0.35 + 40
        min_x, max_x = min_x - pad, max_x + pad
        min_y, max_y = min_y - pad, max_y + pad

        # Match the base aspect so nothing is squashed.
        aspect = WIDTH / HEIGHT
        w, h = max_x - min_x, max_y - min_y
        if w / h < aspect:
            grow = (h * aspect - w) / 2
            min_x, max_x = min_x - grow, max_x + grow
        else:
            grow = (w / aspect - h) / 2
            min_y, max_y = min_y - grow, max_y + grow

        # Never zoom in so far that a camp drifting by a kilometre would look
        # like a serious error — below about half the frame the approximation
        # starts claiming more than it knows.
        if (max_x - min_x) < WIDTH * 0.5:
            cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
            half_w, half_h = WIDTH * 0.25, HEIGHT * 0.25
            min_x, max_x = cx - half_w, cx + half_w
            min_y, max_y = cy - half_h, cy + half_h

        return (f"{min_x:.0f} {min_y:.0f} "
                f"{max_x - min_x:.0f} {max_y - min_y:.0f}")

    def summit(self):
        stages = self.stage_list()
        return max(stages, key=lambda s: s.altitude_m) if stages else None

    def profile(self, width=760, height=250, pad_x=18, pad_top=30, pad_bottom=44):
        """
        Project the camps onto SVG coordinates.

        The vertical scale starts a little below the lowest camp rather than at
        sea level: on a 0-5895 scale every camp between 1600 and 4700 bunches
        into a band and the shape of the climb disappears.
        """
        stages = self.stage_list()
        if len(stages) < 2:
            return {"points": [], "line": "", "area": "", "length": 1}

        highs = [s.altitude_m for s in stages]
        low, high = min(highs), max(highs)
        span = max(high - low, 1)
        floor = low - span * 0.10
        ceiling = high + span * 0.06
        vspan = ceiling - floor

        inner_w = width - pad_x * 2
        inner_h = height - pad_top - pad_bottom

        points = []
        for i, stage in enumerate(stages):
            x = pad_x + (inner_w * i / (len(stages) - 1))
            y = pad_top + inner_h * (1 - (stage.altitude_m - floor) / vspan)
            points.append({"stage": stage, "x": round(x, 1), "y": round(y, 1)})

        line = "M" + " L".join(f"{p['x']},{p['y']}" for p in points)
        base = height - pad_bottom
        area = (f"M{points[0]['x']},{base} L"
                + " L".join(f"{p['x']},{p['y']}" for p in points)
                + f" L{points[-1]['x']},{base} Z")

        length = 0.0
        for a, b in zip(points, points[1:]):
            length += ((b["x"] - a["x"]) ** 2 + (b["y"] - a["y"]) ** 2) ** 0.5

        return {
            "points": points,
            "line": line,
            "area": area,
            "length": round(length * 1.05) or 1,
            "base": base,
            "width": width,
            "height": height,
        }


class ClimbStage(models.Model):
    route = models.ForeignKey(ClimbRoute, on_delete=models.CASCADE, related_name="stages")
    order = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100)
    altitude_m = models.PositiveIntegerField(help_text="Metres above sea level")
    day = models.PositiveIntegerField(blank=True, null=True)

    # Position on the mountain, for the plan-view route map. Seeded from
    # tours/data/kilimanjaro_map.py with approximate figures — see that file.
    latitude = models.FloatField(
        blank=True, null=True,
        help_text="Decimal degrees, negative south of the equator. Leave blank "
                  "and this camp is left off the map rather than guessed at.")
    longitude = models.FloatField(blank=True, null=True, help_text="Decimal degrees.")
    coords_verified = models.BooleanField(
        default=False,
        help_text="Tick once a guide who has walked this camp has confirmed the "
                  "position. While any camp on a route is unticked, the map "
                  "carries a 'positions approximate' note.")

    def map_point(self):
        """SVG coordinates on the Kilimanjaro map, or None if not placed."""
        if self.latitude is None or self.longitude is None:
            return None
        from .data.kilimanjaro_map import project
        return project(self.longitude, self.latitude)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.altitude_m} m)"

    def altitude_ft(self):
        return round(self.altitude_m * 3.28084 / 10) * 10
