from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler(timezone="America/Bogota")
from .tasks import (
    enviar_recordatorios,
    enviar_vacunas_pendientes,
    procesar_correos_pendientes,
)

scheduler = BackgroundScheduler()


def iniciar_scheduler():

    if scheduler.running:
        print("⚠️ Scheduler ya está corriendo")
        return

    scheduler.add_job(
        enviar_recordatorios,
        "interval",
        hours=1,
        id="recordatorios_citas",
        replace_existing=True,
    )

    scheduler.add_job(
        enviar_vacunas_pendientes,
        "interval",
        days=1,
        id="vacunas_pendientes",
        replace_existing=True,
    )

    scheduler.add_job(
        procesar_correos_pendientes,
        "interval",
        minutes=1,
        id="emails_pendientes",
        replace_existing=True,
    )

    scheduler.start()

    print("✅ Scheduler iniciado correctamente")
