# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .models import Especie, Raza, Mascota

class RegistroMascotaTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_redirige_si_no_hay_propietario_en_sesion(self):

        response = self.client.get(
            reverse("mascota:registro_mascota")
        )

        self.assertEqual(response.status_code, 302)

    def test_cargar_razas_retorna_json(self):

        especie = Especie.objects.create(
            nombre="Perro"
        )

        raza = Raza.objects.create(
            nombre="Labrador",
            tipo_especie=especie
        )

        response = self.client.get(
            reverse("mascota:ajax_cargar_razas"),
            {"especie_id": especie.id}
        )

        self.assertEqual(response.status_code, 200)

    def test_cargar_razas_sin_especie(self):

        response = self.client.get(
            reverse("mascota:ajax_cargar_razas")
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            []
        )