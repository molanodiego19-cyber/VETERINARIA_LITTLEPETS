import os
from django.apps import AppConfig

class NotificacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificacion'

    def ready(self):

        # 🔥 evita ejecución doble en modo desarrollo
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .scheduler import iniciar_scheduler
        iniciar_scheduler()