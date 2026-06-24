from django.apps import AppConfig


class NotificacionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notificacion"

    def ready(self):
        try:
            from .scheduler import iniciar_scheduler
            iniciar_scheduler()
        except Exception as e:
            print("❌ Error iniciando scheduler:", e)