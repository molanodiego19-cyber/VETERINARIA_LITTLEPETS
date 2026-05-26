from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import (
    enviar_recordatorios,
    enviar_vacunas_pendientes
)

scheduler = BackgroundScheduler()

def iniciar_scheduler():

    # 🔥 evitar duplicados de jobs
    if scheduler.get_jobs():
        print("⚠️ Scheduler ya estaba iniciado")
        return

    # Recordatorios (cada 1 hora)
    scheduler.add_job(
        enviar_recordatorios,
        'interval',
        hours=1,
        id='recordatorios_citas',
        replace_existing=True
    )

    # Vacunas (cada 24h)
    scheduler.add_job(
        enviar_vacunas_pendientes,
        'interval',
        days=1,
        id='vacunas_pendientes',
        replace_existing=True
    )

    scheduler.start()

    print("✅ Scheduler iniciado correctamente")