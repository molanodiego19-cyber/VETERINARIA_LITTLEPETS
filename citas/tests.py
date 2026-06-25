# Create your tests here.
from django.test import TestCase
from django.urls import reverse

class CitasViewsTest(TestCase):

    def test_index_responde_200(self):

        response = self.client.get(
            reverse("citas:index")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_horarios_disponibles_sin_datos(self):

        response = self.client.get(
            reverse("citas:horarios")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertJSONEqual(
            response.content,
            []
        )

    def test_listar_citas_sin_login(self):

        response = self.client.get(
            reverse("citas:listar")
        )

        self.assertEqual(
            response.status_code,
            302
        )