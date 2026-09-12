from django.apps import AppConfig


class ToursConfig(AppConfig):
    name = 'tours'

    def ready(self):
        # Wires up the navigation cache invalidation.
        from . import signals  # noqa: F401
