from django import forms
from django.utils import timezone
from datetime import datetime, time
from .models import (
    Cita,
    Consulta,
    HistoriaClinica,
    CategoriaServicios,
    Servicio,
    Medicamento,
    Tratamiento,
    Vacuna,
    Vacunacion,
)
from .utils import veterinario_disponible

from mascota.models import Mascota
from usuarios.models import Veterinario, Usuario

# =========================================================
# HORARIOS DISPONIBLES
# =========================================================

HORAS = []

for h in range(7, 20):  # 7:00 AM -> 7:30 PM

    HORAS.append((time(h, 0), f"{h:02d}:00"))

    HORAS.append((time(h, 30), f"{h:02d}:30"))


# =========================================================
# CITA FORM
# =========================================================


class CitaForm(forms.ModelForm):

    class Meta:

        model = Cita

        fields = ["fecha", "hora", "mascota", "servicio", "vacuna", "motivo_consulta"]

        widgets = {
            "fecha": forms.HiddenInput(),
            "hora": forms.HiddenInput(),
        }

    # -----------------------------------------------------
    # FILTRAR MASCOTAS POR USUARIO
    # -----------------------------------------------------

    def __init__(self, *args, **kwargs):

        request = kwargs.pop("request", None)

        propietario_id = kwargs.pop("propietario_id", None)

        print("FORM PROPIETARIO:", propietario_id)

        es_recepcionista = kwargs.pop("es_recepcionista", False)

        super().__init__(*args, **kwargs)

        if propietario_id:
            self.fields["mascota"].queryset = Mascota.objects.filter(
                propietario_id=propietario_id
            )
            return

        if request:
            propietario_id = request.session.get("propietario_id")

            if propietario_id:

                self.fields["mascota"].queryset = Mascota.objects.filter(
                    propietario_id=propietario_id
                )

            else:
                u_id = request.session.get("usuario_id")
                self.fields["mascota"].queryset = Mascota.objects.filter(
                    propietario__usuario_id=u_id
                )

        if es_recepcionista:
            if "mascota" in self.fields:
                del self.fields["mascota"]
        else:
            self.fields["vacuna"].required = False
            self.fields["vacuna"].empty_label = "-- Seleccione la vacuna --"
            self.fields["mascota"].queryset = Mascota.objects.none()

        if request:

            usuario_id = request.session.get("usuario_id")

            if usuario_id:

                try:

                    usuario = Usuario.objects.get(id=usuario_id)

                    if hasattr(usuario, "propietario"):

                        self.fields["mascota"].queryset = Mascota.objects.filter(
                            propietario=usuario.propietario
                        )

                except Usuario.DoesNotExist:
                    pass

    # -----------------------------------------------------
    # VALIDACIONES
    # -----------------------------------------------------

    def clean(self):

        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        servicio = cleaned_data.get("servicio")

        # VALIDAR FECHA/HORA PASADA
        if fecha and hora:

            fecha_hora_cita = datetime.combine(fecha, hora)

            fecha_hora_cita = timezone.make_aware(fecha_hora_cita)

            ahora = timezone.now()

            if fecha_hora_cita < ahora:

                raise forms.ValidationError(
                    "❌ No puedes agendar citas en fechas u horas pasadas"
                )

        # VALIDAR SELECCIÓN
        if not fecha or not hora:

            raise forms.ValidationError("❌ Debes seleccionar un horario")

        # BUSCAR VETERINARIOS
        veterinarios = Veterinario.objects.filter(disponible=True, servicios=servicio)

        if servicio and servicio.especialista_required:

            veterinarios = veterinarios.filter(
                especialidad=servicio.especialista_required
            )

        # VERIFICAR DISPONIBILIDAD
        disponible = False

        for vet in veterinarios:

            if veterinario_disponible(vet, fecha, hora, servicio):

                disponible = True
                break

        if not disponible:

            raise forms.ValidationError("⚠️ Este horario ya no está disponible")

        return cleaned_data


# ========================================================
# FORM PARA CREAR CITA RECEPCIONISTA
# ======================================================}
class CitaRecepcionistaForm(forms.Form):
    fecha = forms.DateField(widget=forms.HiddenInput())
    hora = forms.TimeField(widget=forms.HiddenInput())
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.all(), empty_label="-- Seleccione el servicio --"
    )
    vacuna = forms.ModelChoiceField(
        queryset=Vacuna.objects.all(),
        required=False,
        empty_label="-- Seleccione la vacuna --",
    )
    motivo_consulta = forms.CharField(widget=forms.Textarea(), required=False)

    # Pegamos la lógica de limpieza de horarios aquí, ya que no depende de 'mascota'
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        servicio = cleaned_data.get("servicio")

        if fecha and hora:
            fecha_hora_cita = datetime.combine(fecha, hora)
            fecha_hora_cita = timezone.make_aware(fecha_hora_cita)
            if fecha_hora_cita < timezone.now():
                raise forms.ValidationError(
                    "❌ No puedes agendar citas en fechas u horas pasadas"
                )

        if not fecha or not hora:
            raise forms.ValidationError("❌ Debes seleccionar un horario")

        # Buscar e inspeccionar disponibilidad de veterinarios
        veterinarios = Veterinario.objects.filter(disponible=True, servicios=servicio)
        if servicio and servicio.especialista_required:
            veterinarios = veterinarios.filter(
                especialidad=servicio.especialista_required
            )

        disponible = False
        for vet in veterinarios:
            if veterinario_disponible(vet, fecha, hora, servicio):
                disponible = True
                break

        if not disponible:
            raise forms.ValidationError("⚠️ Este horario ya no está disponible")

        return cleaned_data


# =========================================================
# FORM PARA REAGENDAR CITA
# ========================================================
class ReagendarCitaForm(forms.ModelForm):

    class Meta:

        model = Cita

        fields = ["mascota", "servicio", "fecha", "hora", "motivo_consulta"]

        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "motivo_consulta": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    # ==========================================
    # BLOQUEAR CAMPOS
    # ==========================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["mascota"].disabled = True
        self.fields["servicio"].disabled = True

    # ==========================================
    # VALIDACIONES
    # ==========================================

    def clean(self):

        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        servicio = cleaned_data.get("servicio")

        # --------------------------------------
        # VALIDAR FECHA PASADA
        # --------------------------------------

        if fecha and hora:

            fecha_hora = datetime.combine(fecha, hora)

            fecha_hora = timezone.make_aware(fecha_hora)

            if fecha_hora < timezone.now():

                raise forms.ValidationError("❌ No puedes reagendar citas en el pasado")

        # --------------------------------------
        # VALIDAR DISPONIBILIDAD
        # --------------------------------------

        veterinarios = Veterinario.objects.filter(disponible=True, servicios=servicio)

        disponible = False

        for vet in veterinarios:

            if veterinario_disponible(vet, fecha, hora, servicio):

                disponible = True
                break

        if not disponible:

            raise forms.ValidationError(
                "⚠️ No hay veterinarios disponibles en ese horario"
            )

        return cleaned_data


# =========================================================
# CONSULTA FORM SIMPLE
# =========================================================


class ConsultaForm(forms.ModelForm):

    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )

    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )

    class Meta:

        model = Consulta

        exclude = ["fecha_creacion"]

        widgets = {
            "anamnesis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "examen_fisico": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "diagnostico_presuntivo": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "diagnostico_definitivo": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "plan_terapeutico": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "peso_en_consulta": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "temperatura": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),
            "frecuencia_cardiaca": forms.NumberInput(attrs={"class": "form-control"}),
            "frecuencia_respiratoria": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }

    # ==========================================
    # VALIDAR HORAS
    # ==========================================

    def clean(self):

        cleaned_data = super().clean()

        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if hora_inicio and hora_fin:

            if hora_fin <= hora_inicio:

                self.add_error(
                    "hora_fin", "La hora final debe ser mayor que la hora inicial."
                )

        return cleaned_data


# =========================================================
# CONSULTA COMPLETA FORM
# =========================================================


class ConsultaCompletaForm(ConsultaForm):

    class Meta(ConsultaForm.Meta):

        model = Consulta

        exclude = ["fecha_creacion", "cita", "veterinario"]


# =========================================================
# HISTORIA CLINICA
# =========================================================


class HistoriaClinicaForm(forms.ModelForm):

    class Meta:

        model = HistoriaClinica

        exclude = ["fecha_creacion", "fecha_actualizacion"]

        widgets = {
            "fecha_consulta": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "motivo_consulta": forms.TextInput(attrs={"class": "form-control"}),
            "diagnostico": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tratamiento": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# =========================================================
# CATEGORIA SERVICIOS
# =========================================================


class CategoriaServiciosForm(forms.ModelForm):

    class Meta:

        model = CategoriaServicios

        fields = "__all__"

        widgets = {
            "nombre_categoria": forms.TextInput(attrs={"class": "form-control"}),
        }


# =========================================================
# SERVICIO
# =========================================================


class ServicioForm(forms.ModelForm):

    class Meta:

        model = Servicio

        fields = "__all__"

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "precio": forms.NumberInput(attrs={"class": "form-control"}),
            "duracion_minutos": forms.NumberInput(attrs={"class": "form-control"}),
        }


# =========================================================
# MEDICAMENTO
# =========================================================


class MedicamentoForm(forms.ModelForm):

    class Meta:

        model = Medicamento

        fields = "__all__"

        widgets = {
            "nombre_comercial": forms.TextInput(attrs={"class": "form-control"}),
            "presentacion": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_vencimiento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }


# =========================================================
# TRATAMIENTO
# =========================================================
class TratamientoForm(forms.ModelForm):

    class Meta:

        model = Tratamiento

        exclude = ["consulta", "veterinario", "fecha_creacion"]

        widgets = {
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "medicamento": forms.TextInput(attrs={"class": "form-control"}),
            "dosis": forms.NumberInput(attrs={"class": "form-control"}),
            "frecuencia": forms.TextInput(attrs={"class": "form-control"}),
            "instrucciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "duracion_dias": forms.NumberInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    # ==========================================
    # VALIDAR FECHAS
    # ==========================================

    def clean(self):

        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        hoy = timezone.localdate()

        # VALIDAR FECHA INICIO
        if fecha_inicio and fecha_inicio < hoy:

            self.add_error("fecha_inicio", "La fecha de inicio no puede ser pasada.")

        # VALIDAR FECHA FIN
        if fecha_fin and fecha_fin < hoy:

            self.add_error("fecha_fin", "La fecha final no puede ser pasada.")

        # VALIDAR ORDEN DE FECHAS
        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:

                self.add_error(
                    "fecha_fin",
                    "La fecha final debe ser mayor o igual a la fecha inicial.",
                )

        return cleaned_data


# =========================================================
# VACUNA
# =========================================================


class VacunaForm(forms.ModelForm):

    class Meta:

        model = Vacuna
        fields = "__all__"

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "especie": forms.Select(attrs={"class": "form-select"}),
            "enfermedad_objetivo": forms.TextInput(attrs={"class": "form-control"}),
            "precio_adquisicion": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "precio_venta": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "laboratorio": forms.TextInput(attrs={"class": "form-control"}),
            "dosis_total": forms.NumberInput(attrs={"class": "form-control"}),
            "lote": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# =========================================================
# VACUNACION
# =========================================================
class VacunacionForm(forms.ModelForm):

    class Meta:

        model = Vacunacion

        fields = [
            "vacuna",
            "numero_dosis",
            "proxima_dosis",
            "peso_actual",
            "observaciones",
        ]

        widgets = {
            "vacuna": forms.Select(attrs={"class": "form-select"}),
            "numero_dosis": forms.NumberInput(attrs={"class": "form-control"}),
            "proxima_dosis": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "peso_actual": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
