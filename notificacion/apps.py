from django.apps import AppConfig


class NotificacionConfig(AppConfig):
    name = "notificacion"

    def ready(self):
        pass  # NO iniciar scheduler aquí directamente