from django.apps import AppConfig


class ResearchersConfig(AppConfig):
    name = 'researchers'

    def ready(self):
        import researchers.signals