from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from tours import views as tour_views
from tours.sitemaps import (
    CategorySitemap, DestinationSitemap, PackageSitemap, StaticViewSitemap,
)

sitemaps = {
    "static": StaticViewSitemap,
    "packages": PackageSitemap,
    "categories": CategorySitemap,
    "destinations": DestinationSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", tour_views.robots_txt, name="robots_txt"),
    path("", include("tours.urls")),
]

# Media is served locally only; in production it lives in the Supabase bucket.
if settings.DEBUG and hasattr(settings, "MEDIA_ROOT"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
