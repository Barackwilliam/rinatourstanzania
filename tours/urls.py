from django.urls import path

from . import views

app_name = "tours"

urlpatterns = [
    path("", views.home, name="home"),

    path("tours/", views.package_list, name="package_list"),
    path("tours/all/", views.package_index, name="package_index"),
    path("tours/<slug:slug>/", views.package_detail, name="package_detail"),

    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),

    path("destinations/", views.destination_list, name="destination_list"),
    path("destinations/<slug:slug>/", views.destination_detail, name="destination_detail"),

    path("day-trips/", views.day_trip_list, name="day_trip_list"),
    path("transfers/", views.transfers, name="transfers"),
    path("stay/", views.stay, name="stay"),

    path("about/", views.about, name="about"),
    path("reviews/", views.reviews, name="reviews"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),

    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-and-conditions/", views.terms, name="terms"),
]
