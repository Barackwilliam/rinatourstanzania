"""
Put three starter slides in the homepage hero.

    python manage.py seed_hero

They carry no photographs — the hero falls back to tonal panels, so the
carousel is visibly working before the client sends imagery. Open each slide in
the admin, attach an image or a short muted clip, and the same slide becomes
the real thing. Existing slides are left alone unless you pass --replace.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.models import Category, HeroSlide, Package

SLIDES = [
    {
        "eyebrow": "Refined in delivery",
        "headline": "Let's design your Tanzania",
        "headline_script": "your way",
        "subline": "Savannah, mountain or sea — tell us what moves you and we'll build the rest.",
        "cta_label": "Start planning",
        "cta_name": "contact",
    },
    {
        "eyebrow": "Northern circuit",
        "headline": "Big cat country",
        "headline_script": "up close",
        "subline": "Private drives through the Serengeti, Tarangire and the Ngorongoro Crater.",
        "cta_label": "See safari tours",
        "cta_category": "Safari / Wildlife Tours",
    },
    {
        "eyebrow": "Roof of Africa",
        "headline": "Kilimanjaro, then the coast",
        "headline_script": "at your own pace",
        "subline": "Safe routes and patient guides, followed by a week on the Indian Ocean.",
        "cta_label": "See treks",
        "cta_category": "Trekking / Mountain Climbing",
    },
]


class Command(BaseCommand):
    help = "Create three starter hero slides."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace", action="store_true",
            help="Delete existing slides first. Uploaded images are lost.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["replace"]:
            HeroSlide.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing slides deleted."))
        elif HeroSlide.objects.exists():
            self.stdout.write(
                f"{HeroSlide.objects.count()} slides already exist — leaving them alone. "
                "Pass --replace to start over.")
            return

        for order, spec in enumerate(SLIDES):
            url = "/contact/"
            if spec.get("cta_category"):
                category = Category.objects.filter(name=spec["cta_category"]).first()
                if category:
                    url = category.get_absolute_url()
            HeroSlide.objects.create(
                eyebrow=spec["eyebrow"],
                headline=spec["headline"],
                headline_script=spec["headline_script"],
                subline=spec["subline"],
                cta_label=spec["cta_label"],
                cta_url=url,
                order=order,
                active=True,
            )
            self.stdout.write(f"  slide  {spec['headline']}")

        self.stdout.write(self.style.SUCCESS(
            f"\n{HeroSlide.objects.count()} slides. Add an image to each one in the "
            f"admin — until then the hero uses tonal panels."))
