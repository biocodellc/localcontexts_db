from django.apps import AppConfig


class BclabelsConfig(AppConfig):
    name = 'bclabels'

    def ready(self):
        import bclabels.signals
