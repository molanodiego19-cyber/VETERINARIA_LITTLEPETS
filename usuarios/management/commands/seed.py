from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from usuarios.models import (
    Usuario,
    Administrador,
    Propietario,
    Veterinario
)
from datetime import datetime, date
from veterinarioapp.models import Especialidad
from mascota.models import Especie, Raza, Mascota
from citas.models import CategoriaServicios, Servicio,Vacuna
from notificacion.models import PlantillaNotificacion


class Command(BaseCommand):

    help = "Seeder completo del sistema veterinario"

    def handle(self, *args, **kwargs):

        if Usuario.objects.exists():
            self.stdout.write("⚠️ Ya existen datos, seed cancelado")
            return

        # =====================================================
        # ADMIN
        # =====================================================

        admin_user = Usuario.objects.create(
            correo="admin@gmail.com",
            password=make_password("123456"),
            rol=Usuario.Rol.ADMIN,
            estado=Usuario.Estado.ACTIVO
        )

        Administrador.objects.create(
            usuario=admin_user,
            nombre="Dahian",
            apellido="Reina",
            telefono="3000000000",
            tipo_documento="CC",
            documento="9999999999"
        )

        # =====================================================
        # ESPECIALIDADES
        # =====================================================

        cirugia = Especialidad.objects.create(
            nombre="Cirugía",
            descripcion="Procedimientos quirúrgicos"
        )

        dermatologia = Especialidad.objects.create(
            nombre="Dermatología",
            descripcion="Enfermedades de piel"
        )

        cardiologia = Especialidad.objects.create(
            nombre="Cardiología",
            descripcion="Corazón y sistema circulatorio"
        )

        odontologia_esp = Especialidad.objects.create(
            nombre="Odontología",
            descripcion="Salud dental animal"
        )

        diagnostico_img = Especialidad.objects.create(
            nombre="Diagnóstico por Imágenes",
            descripcion="Ecografías y estudios"
        )

        medicina_general = Especialidad.objects.create(
            nombre="Medicina General",
            descripcion="Atención primaria veterinaria"
        )

        estetica_esp = Especialidad.objects.create(
            nombre="Estética Animal",
            descripcion="Baño y peluquería"
        )

        laboratorio_clinico = Especialidad.objects.create(
            nombre="Laboratorio Clínico",
            descripcion="Análisis clínicos"
        )

        # =====================================================
        # CATEGORÍAS
        # =====================================================

        consulta = CategoriaServicios.objects.create(
            nombre_categoria="Consulta General"
        )

        cirugia_cat = CategoriaServicios.objects.create(
            nombre_categoria="Cirugía"
        )

        vacunacion = CategoriaServicios.objects.create(
            nombre_categoria="Vacunación"
        )

        diagnostico = CategoriaServicios.objects.create(
            nombre_categoria="Diagnóstico"
        )

        laboratorio = CategoriaServicios.objects.create(
            nombre_categoria="Laboratorio"
        )

        odontologia_cat = CategoriaServicios.objects.create(
            nombre_categoria="Odontología"
        )

        estetica = CategoriaServicios.objects.create(
            nombre_categoria="Estética y Baño"
        )

        # =====================================================
        # SERVICIOS
        # =====================================================

        consulta_general = Servicio.objects.create(
            nombre="Consulta General",
            descripcion="Revisión médica general",
            precio=50000,
            duracion_minutos=30,
            categoria=consulta,
            especialista_required=medicina_general
        )

        vacuna = Servicio.objects.create(
            nombre="Vacuna Antirrábica",
            descripcion="Prevención de rabia",
            precio=30000,
            duracion_minutos=15,
            categoria=vacunacion,
            especialista_required=medicina_general
        )

        ecografia = Servicio.objects.create(
            nombre="Ecografía",
            descripcion="Diagnóstico por imágenes",
            precio=90000,
            duracion_minutos=40,
            categoria=diagnostico,
            especialista_required=diagnostico_img
        )

        examen_sangre = Servicio.objects.create(
            nombre="Examen de Sangre",
            descripcion="Hemograma completo",
            precio=60000,
            duracion_minutos=20,
            categoria=laboratorio,
            especialista_required=laboratorio_clinico
        )

        esterilizacion = Servicio.objects.create(
            nombre="Esterilización",
            descripcion="Cirugía de esterilización",
            precio=180000,
            duracion_minutos=90,
            categoria=cirugia_cat,
            especialista_required=cirugia
        )

        limpieza_dental = Servicio.objects.create(
            nombre="Limpieza Dental",
            descripcion="Profilaxis dental",
            precio=70000,
            duracion_minutos=45,
            categoria=odontologia_cat,
            especialista_required=odontologia_esp
        )

        bano = Servicio.objects.create(
            nombre="Baño y Peluquería",
            descripcion="Baño completo de mascota",
            precio=50000,
            duracion_minutos=60,
            categoria=estetica,
            especialista_required=estetica_esp
        )

        
        # =====================================================
        # VETERINARIOS
        # =====================================================

        veterinarios_data = [
            {
                "nombre": "Rosa",
                "apellido": "Sichaca",
                "correo": "rosa@gmail.com",
                "telefono": "3001111111",
                "documento": "2000000001",
                "licencia": "VET001",
                "especialidad": cirugia,
                "servicios": [esterilizacion],
                "dias": ["miercoles", "jueves", "viernes", "sabado", "domingo"]
            },
            {
                "nombre": "Andrea",
                "apellido": "Molano",
                "correo": "andrea@gmail.com",
                "telefono": "3002222222",
                "documento": "2000000002",
                "licencia": "VET002",
                "especialidad": dermatologia,
                "servicios": [],
                "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]
            },
            {
                "nombre": "Carlos",
                "apellido": "Ramírez",
                "correo": "carlos@gmail.com",
                "telefono": "3003333333",
                "documento": "2000000003",
                "licencia": "VET003",
                "especialidad": cardiologia,
                "servicios": [],
                "dias": ["lunes", "martes", "miercoles"]
            },
            {
                "nombre": "Luisa",
                "apellido": "Fernández",
                "correo": "luisa@gmail.com",
                "telefono": "3004444444",
                "documento": "2000000004",
                "licencia": "VET004",
                "especialidad": odontologia_esp,
                "servicios": [limpieza_dental],
                "dias": ["jueves", "viernes", "sabado"]
            },
            {
                "nombre": "Miguel",
                "apellido": "Castro",
                "correo": "miguel@gmail.com",
                "telefono": "3005555555",
                "documento": "2000000005",
                "licencia": "VET005",
                "especialidad": diagnostico_img,
                "servicios": [ecografia],
                "dias": ["lunes", "martes", "viernes"]
            },
            {
                "nombre": "Valentina",
                "apellido": "Torres",
                "correo": "valentina@gmail.com",
                "telefono": "3006666666",
                "documento": "2000000006",
                "licencia": "VET006",
                "especialidad": medicina_general,
                "servicios": [consulta_general, vacuna],
                "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]
            },
            {
                "nombre": "Santiago",
                "apellido": "Morales",
                "correo": "santiago@gmail.com",
                "telefono": "3007777777",
                "documento": "2000000007",
                "licencia": "VET007",
                "especialidad": estetica_esp,
                "servicios": [bano],
                "dias": ["sabado", "domingo"]
            },
            {
                "nombre": "Paula",
                "apellido": "Gómez",
                "correo": "paula@gmail.com",
                "telefono": "3008888888",
                "documento": "2000000008",
                "licencia": "VET008",
                "especialidad": laboratorio_clinico,
                "servicios": [examen_sangre],
                "dias": ["lunes", "miercoles", "viernes"]
            },
        ]

        for vet in veterinarios_data:

            user = Usuario.objects.create(
                correo=vet["correo"],
                password=make_password("123456"),
                rol=Usuario.Rol.VETERINARIO,
                estado=Usuario.Estado.ACTIVO
            )

            veterinario = Veterinario.objects.create(
                usuario=user,
                nombre=vet["nombre"],
                apellido=vet["apellido"],
                telefono=vet["telefono"],
                tipo_documento="CC",
                documento=vet["documento"],
                especialidad=vet["especialidad"],
                num_licencia=vet["licencia"],
                dias_laborales=vet["dias"]
            )

            veterinario.servicios.set(vet["servicios"])

        # =====================================================
        # PROPIETARIOS
        # =====================================================

        propietarios = []

        datos = [
            ("Diego", "Martínez", "3001110001", "1000000001"),
            ("María", "Rodríguez", "3002220002", "1000000002"),
            ("Juan", "López", "3003330003", "1000000003"),
            ("Laura", "García", "3004440004", "1000000004"),
            ("Andrés", "Hernández", "3005550005", "1000000005"),
            ("Sofía", "Torres", "3006660006", "1000000006"),
        ]

        for i, (n, a, tel, doc) in enumerate(datos):

            user = Usuario.objects.create(
                correo=f"{n.lower()}{i}@gmail.com",
                password=make_password("123456"),
                rol=Usuario.Rol.PROPIETARIO,
                estado=Usuario.Estado.ACTIVO
            )

            prop = Propietario.objects.create(
                usuario=user,
                nombre=n,
                apellido=a,
                telefono=tel,
                tipo_documento="CC",
                documento=doc,
                ciudad="Bogotá",
                direccion="Calle Principal 123"
            )

            propietarios.append(prop)

        # =====================================================
        # ESPECIES
        # =====================================================

        perro = Especie.objects.create(
            nombre="Perro",
            descripcion="Canino doméstico"
        )

        gato = Especie.objects.create(
            nombre="Gato",
            descripcion="Felino doméstico"
        )

        # =====================================================
        # RAZAS
        # =====================================================

        lab = Raza.objects.create(
            nombre="Labrador",
            tipo_especie=perro
        )

        pastor = Raza.objects.create(
            nombre="Pastor Alemán",
            tipo_especie=perro
        )

        siames = Raza.objects.create(
            nombre="Siamés",
            tipo_especie=gato
        )

        angora = Raza.objects.create(
            nombre="Angora",
            tipo_especie=gato
        )

        # =====================================================
        # VACUNAS
        # =====================================================

        Vacuna.objects.create(
            nombre="RabiaVet",
            fabricante="Zoetis",
            especie_objetivo=perro,
            enfermedades="Rabia",
            dosis_total=1,
            intervalo_dosis=365,
            refuerzo_meses=12,
            edad_minima_dias=90,
            requiere_frio=True,
            lote="RAB-2026-001",
            fecha_vencimiento=date(2027, 5, 10),
            activo=True,
            fecha_creacion=datetime.now()
        )

        Vacuna.objects.create(
            nombre="Triple Felina",
            fabricante="Merial",
            especie_objetivo=gato,
            enfermedades="Panleucopenia, Rinotraqueitis, Calicivirus",
            dosis_total=2,
            intervalo_dosis=21,
            refuerzo_meses=12,
            edad_minima_dias=60,
            requiere_frio=True,
            lote="FEL-2026-002",
            fecha_vencimiento=date(2027, 8, 15),
            activo=True,
            fecha_creacion=datetime.now()
        )

        Vacuna.objects.create(
            nombre="ParvoCan",
            fabricante="Boehringer",
            especie_objetivo=perro,
            enfermedades="Parvovirus Canino",
            dosis_total=3,
            intervalo_dosis=21,
            refuerzo_meses=12,
            edad_minima_dias=45,
            requiere_frio=True,
            lote="PAR-2026-003",
            fecha_vencimiento=date(2027, 1, 20),
            activo=True,
            fecha_creacion=datetime.now()
        )

        Vacuna.objects.create(
            nombre="Moquillo Plus",
            fabricante="Virbac",
            especie_objetivo=perro,
            enfermedades="Moquillo Canino",
            dosis_total=2,
            intervalo_dosis=30,
            refuerzo_meses=12,
            edad_minima_dias=50,
            requiere_frio=True,
            lote="MOQ-2026-004",
            fecha_vencimiento=date(2027, 3, 5),
            activo=True,
            fecha_creacion=datetime.now()
        )

        Vacuna.objects.create(
            nombre="Leucemia Felina",
            fabricante="Pfizer Animal Health",
            especie_objetivo=gato,
            enfermedades="Leucemia Felina",
            dosis_total=2,
            intervalo_dosis=30,
            refuerzo_meses=12,
            edad_minima_dias=56,
            requiere_frio=True,
            lote="LEU-2026-005",
            fecha_vencimiento=date(2027, 11, 12),
            activo=True,
            fecha_creacion=datetime.now()
        )


        # =====================================================
        # MASCOTAS
        # =====================================================

        Mascota.objects.create(
            propietario=propietarios[0],
            nombre="Max",
            especie=perro,
            raza=lab,
            fecha_nacimiento="2020-05-10",
            sexo="macho",
            peso_kg=25.50,
            esterilizacion=True
        )

        Mascota.objects.create(
            propietario=propietarios[0],
            nombre="Luna",
            especie=gato,
            raza=siames,
            fecha_nacimiento="2021-03-12",
            sexo="hembra",
            peso_kg=4.20
        )

        Mascota.objects.create(
            propietario=propietarios[1],
            nombre="Rocky",
            especie=perro,
            raza=pastor,
            fecha_nacimiento="2019-07-01",
            sexo="macho",
            peso_kg=30
        )

        Mascota.objects.create(
            propietario=propietarios[1],
            nombre="Mia",
            especie=gato,
            raza=siames,
            fecha_nacimiento="2022-01-10",
            sexo="hembra",
            peso_kg=3.80
        )

        Mascota.objects.create(
            propietario=propietarios[2],
            nombre="Toby",
            especie=perro,
            raza=lab,
            fecha_nacimiento="2020-11-12",
            sexo="macho",
            peso_kg=22
        )

        Mascota.objects.create(
            propietario=propietarios[2],
            nombre="Nala",
            especie=perro,
            raza=pastor,
            fecha_nacimiento="2021-06-30",
            sexo="hembra",
            peso_kg=24
        )

        Mascota.objects.create(
            propietario=propietarios[3],
            nombre="Bruno",
            especie=perro,
            raza=lab,
            fecha_nacimiento="2020-08-08",
            sexo="macho",
            peso_kg=27
        )

        # =====================================================
        # PLANTILLAS NOTIFICACIONES
        # =====================================================

        PlantillaNotificacion.objects.create(
            canal='email',
            nombre='cita_agendada',
            asunto_plantilla='✅ Cita agendada correctamente',
            cuerpo_plantilla='''
            <h2>Hola {{ nombre }} 👋</h2>

            <p>Tu cita fue agendada correctamente.</p>

            <p><strong>Mascota:</strong> {{ mascota }}</p>
            <p><strong>Fecha:</strong> {{ fecha }}</p>
            <p><strong>Hora:</strong> {{ hora }}</p>
            <p><strong>Servicio:</strong> {{ servicio }}</p>
            <p><strong>Veterinario:</strong> {{ veterinario }}</p>
            ''',
            activo=True
        )

        PlantillaNotificacion.objects.create(
            canal='email',
            nombre='recordatorio_cita',
            asunto_plantilla='⏰ Recordatorio de cita veterinaria',
            cuerpo_plantilla='''
            <h2>Hola {{ nombre }} ⏰</h2>

            <p>Te recordamos que mañana tienes una cita veterinaria.</p>
            ''',
            activo=True
        )

        PlantillaNotificacion.objects.create(
            canal='email',
            nombre='cuenta_creada',
            asunto_plantilla='🎉 Bienvenido a Little Pets',
            cuerpo_plantilla='''
            <h2>Bienvenido {{ nombre }} 🎉</h2>

            <p>Tu cuenta fue creada correctamente.</p>

            <p><strong>Correo:</strong> {{ correo }}</p>
            ''',
            activo=True
        )

        PlantillaNotificacion.objects.create(
            canal='email',
            nombre='vacuna_pendiente',
            asunto_plantilla='💉 Vacuna pendiente',
            cuerpo_plantilla='''
            <h2>Hola {{ nombre }} 💉</h2>

            <p>Tu mascota tiene vacunas pendientes.</p>
            ''',
            activo=True
        )

        PlantillaNotificacion.objects.create(
            canal='email',
            nombre='cita_cancelada',
            asunto_plantilla='❌ Cita cancelada con éxito',
            cuerpo_plantilla='''
            <h2>Hola {{ nombre }} ❌</h2>

            <p>Tu cita fue cancelada con éxito.</p>

            <hr>

            <h3>📅 Detalles de la cita cancelada</h3>

            <ul>
                <li><strong>Mascota:</strong> {{ mascota }}</li>
                <li><strong>Servicio:</strong> {{ servicio }}</li>
                <li><strong>Fecha:</strong> {{ fecha }}</li>
                <li><strong>Hora:</strong> {{ hora }}</li>
                <li><strong>Veterinario:</strong> {{ veterinario }}</li>
            </ul>

            <p>Si lo necesitas, puedes reagendar una nueva cita 🐾</p>
            ''',
            activo=True
        )

        self.stdout.write(
            self.style.SUCCESS("✅ SEED COMPLETO EJECUTADO")
        )