from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Destination, Package


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return [
            "tours:home", "tours:package_list", "tours:category_list",
            "tours:destination_list", "tours:day_trip_list", "tours:transfers",
            "tours:about", "tours:reviews", "tours:faq", "tours:contact",
        ]

    def location(self, item):
        return reverse(item)


class PackageSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Package.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Category.objects.all()


class DestinationSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Destination.objects.all()
