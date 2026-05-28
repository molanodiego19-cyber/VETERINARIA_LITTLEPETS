from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import (
    enviar_recordatorios,
    enviar_vacunas_pendientes,
    procesar_correos_pendientes
)

# 🔥 crear scheduler primero
scheduler = BackgroundScheduler()


def iniciar_scheduler():

    # 🔥 evitar duplicados
    if scheduler.get_jobs():
        print("⚠️ Scheduler ya estaba iniciado")
        return

    # =====================================================
    # RECORDATORIOS
    # =====================================================

    scheduler.add_job(
        enviar_recordatorios,
        'interval',
        hours=1,
        id='recordatorios_citas',
        replace_existing=True
    )

    # =====================================================
    # VACUNAS PENDIENTES
    # =====================================================

    scheduler.add_job(
        enviar_vacunas_pendientes,
        'interval',
        days=1,
        id='vacunas_pendientes',
        replace_existing=True
    )

    # =====================================================
    # CORREOS PENDIENTES
    # =====================================================

    scheduler.add_job(
        procesar_correos_pendientes,
        'interval',
        minutes=1,
        id='emails_pendientes',
        replace_existing=True
    )

    # 🔥 iniciar scheduler
    scheduler.start()

    print("✅ Scheduler iniciado correctamente")