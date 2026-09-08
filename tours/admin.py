from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category, Destination, Package, ItineraryDay, PackageImage, HeroSlide,
    MapRoute, RouteStop, TransferService, Testimonial, TeamMember, FAQ,
    ContactMessage,
)


class ItineraryDayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 1


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "bead", "package_count", "order", "featured")
    list_editable = ("order", "featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "code")

    @admin.display(description="bead")
    def bead(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;'
            'border-radius:50%;background:{}"></span>', obj.bead_colour)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "package_count", "geocoded", "order", "featured")
    list_editable = ("region", "order", "featured")
    list_filter = ("region", "featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "aliases")

    @admin.display(description="packages")
    def package_count(self, obj):
        return obj.packages.count()

    @admin.display(boolean=True, description="on map")
    def geocoded(self, obj):
        return obj.latitude is not None


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "title", "primary_category", "duration_display", "price_display",
        "ready", "featured", "published",
    )
    list_filter = ("primary_category", "categories", "published", "featured", "price_basis")
    list_editable = ("featured", "published")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories", "destinations")
    inlines = [ItineraryDayInline, PackageImageInline]

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "primary_category", "categories",
                       "published", "featured", "order")
        }),
        ("Duration & route", {
            "fields": ("duration_days", "duration_nights", "duration_text",
                       "starting_point", "destinations", "route")
        }),
        ("Price", {"fields": ("price_from", "currency", "price_basis")}),
        ("Copy", {
            "fields": ("short_description", "description", "highlights",
                       "includes", "excludes", "best_for", "important_note")
        }),
        ("Media", {"fields": ("image", "image_upload", "video")}),
    )

    @admin.display(boolean=True, description="ready to sell")
    def ready(self, obj):
        return obj.is_complete()


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    autocomplete_fields = ["destination"]


@admin.register(MapRoute)
class MapRouteAdmin(admin.ModelAdmin):
    list_display = ("name", "swatch", "stop_count", "package", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [RouteStopInline]

    @admin.display(description="colour")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:34px;height:12px;'
            'border-radius:2px;background:{}"></span>', obj.colour)

    @admin.display(description="stops")
    def stop_count(self, obj):
        return obj.stops.count()


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("headline", "has_video", "order", "active")
    list_editable = ("order", "active")
    list_filter = ("active",)


@admin.register(TransferService)
class TransferServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_country", "rating", "package", "featured")
    list_editable = ("featured",)
    list_filter = ("rating", "featured")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "order", "active")
    list_editable = ("order", "active")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "order")
    list_editable = ("order",)
    list_filter = ("category",)
    search_fields = ("question", "answer")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "package", "travel_date",
                    "created_at", "handled")
    list_editable = ("handled",)
    list_filter = ("handled", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)


admin.site.site_header = f"{settings.SITE_NAME} Admin"
admin.site.site_title = f"{settings.SITE_NAME} Admin"
admin.site.index_title = "Content dashboard"
