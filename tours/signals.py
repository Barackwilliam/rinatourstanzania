"""
Cache invalidation for the header/footer navigation.

The menus are cached so the six queries behind them are not paid on every page
load. That is only safe if an admin edit clears the entry immediately — a TTL
alone would mean the client saves a change and then does not see it, which
reads as "the site is broken" rather than "the cache has not expired yet".
"""

from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .context_processors import NAV_CACHE_KEY
from .models import Category, Destination, Package


def _clear(**kwargs):
    cache.delete(NAV_CACHE_KEY)


for model in (Category, Destination, Package):
    post_save.connect(_clear, sender=model, dispatch_uid=f"nav-save-{model.__name__}")
    post_delete.connect(_clear, sender=model, dispatch_uid=f"nav-del-{model.__name__}")

# Tour counts in the menu come from the M2M, which does not fire post_save.
m2m_changed.connect(
    _clear, sender=Package.categories.through, dispatch_uid="nav-m2m-categories")
m2m_changed.connect(
    _clear, sender=Package.destinations.through, dispatch_uid="nav-m2m-destinations")
