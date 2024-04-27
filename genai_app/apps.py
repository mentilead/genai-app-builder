from django.apps import AppConfig


class GenaiAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "genai_app"

    def ready(self):
        import genai_app.signals  # noqa: F401 to register signals
