from django.test import TestCase
from .forms import PropietarioCompletoForm
from .models import Propietario, Usuario


class PropietarioFormTest(TestCase):

    def setUp(self):
        self.datos_validos = {
            "nombre": "juan",
            "apellido": "perez",
            "telefono": "3001234567",
            "tipo_documento": "CC",
            "documento": "1234567890",
            "ciudad": "Bogota",
            "direccion": "Calle 123",
            "correo": "test@test.com",
            "password": "12345678",
            "foto": None,  
        }

    # ✅ FORMULARIO VÁLIDO
    def test_form_valido(self):
        form = PropietarioCompletoForm(data=self.datos_validos)

        print(form.errors) 

        self.assertTrue(form.is_valid())

    # ✅ NOMBRE EN MAYÚSCULA
    def test_nombre_se_convierte_a_mayuscula(self):
        form = PropietarioCompletoForm(data=self.datos_validos)
        self.assertTrue(form.is_valid())

        propietario = form.save()
        self.assertEqual(propietario.nombre.upper(), "JUAN")

    # ❌ TELÉFONO INVÁLIDO
    def test_telefono_invalido(self):
        datos = self.datos_validos.copy()
        datos["telefono"] = "abc123"

        form = PropietarioCompletoForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    # ❌ CORREO DUPLICADO
    def test_correo_duplicado(self):
        Usuario.objects.create(correo="test@test.com", password="123")

        form = PropietarioCompletoForm(data=self.datos_validos)
        self.assertFalse(form.is_valid())
        self.assertIn("correo", form.errors)

    # ❌ DOCUMENTO DUPLICADO (CORREGIDO)
    def test_documento_duplicado(self):
        usuario = Usuario.objects.create(correo="otro@test.com", password="123456")

        Propietario.objects.create(
            usuario=usuario,  # 👈 obligatorio
            nombre="Juan",
            apellido="Perez",
            telefono="3000000000",
            tipo_documento="CC",
            documento="1234567890",
            ciudad="Bogota",
            direccion="Calle 1",
        )

        form = PropietarioCompletoForm(data=self.datos_validos)
        self.assertFalse(form.is_valid())
        self.assertIn("documento", form.errors)
