"""
Apply the operator's ordering and featured selection.

    python manage.py apply_priorities

Reads tours/data/priorities.py. Safe to re-run, and safe to run after a
re-import: it only touches ordering and the featured flag.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from tours.data.priorities import CATEGORY_ORDER, FEATURED_SLUGS
from tours.models import Category, Package


class Command(BaseCommand):
    help = "Order categories and set the featured tours."

    @transaction.atomic
    def handle(self, *args, **options):
        # --- category order ---------------------------------------------
        for i, name in enumerate(CATEGORY_ORDER):
            updated = Category.objects.filter(name=name).update(order=i)
            if not updated:
                self.stdout.write(self.style.WARNING(
                    f"  no category named {name!r} — check the spelling"))

        unlisted = Category.objects.exclude(name__in=CATEGORY_ORDER)
        for i, category in enumerate(unlisted, start=len(CATEGORY_ORDER)):
            category.order = i
            category.save(update_fields=["order"])

        self.stdout.write("  category order:")
        for c in Category.objects.all():
            self.stdout.write(f"    {c.order}. {c.name}")

        # --- featured tours ----------------------------------------------
        Package.objects.filter(featured=True).update(featured=False)

        found = 0
        self.stdout.write("\n  featured on the homepage:")
        for i, slug in enumerate(FEATURED_SLUGS):
            package = Package.objects.filter(slug=slug).first()
            if package is None:
                self.stdout.write(self.style.WARNING(
                    f"    no tour with slug {slug!r} — skipped"))
                continue
            package.featured = True
            package.order = i
            package.save(update_fields=["featured", "order"])
            self.stdout.write(f"    {i + 1}. {package.title}")
            found += 1

        if not found:
            self.stdout.write(self.style.ERROR(
                "\n  Nothing was featured. The homepage row will stay hidden."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\n{found} tours featured, {Category.objects.count()} categories ordered."))
