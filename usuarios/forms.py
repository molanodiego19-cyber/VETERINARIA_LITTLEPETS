from django import forms
from django.db import transaction
from .models import Usuario, Administrador, Propietario, Veterinario
from django.contrib.auth.hashers import make_password
from citas.models import Servicio
import re
from django.utils import timezone
from django import forms

# -------------------------
# USUARIO
# -------------------------
class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['correo', 'password', 'rol']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        # 🔐 ENCRIPTAR CONTRASEÑA
        usuario.password = make_password(self.cleaned_data['password'])

        if commit:
            usuario.save()

        return usuario


# -------------------------
# ADMINISTRADOR
# -------------------------
class AdministradorForm(forms.ModelForm):

    class Meta:
        model = Administrador
        fields = [
            'usuario',
            'nombre',
            'apellido',
            'telefono',
            'tipo_documento',
            'documento',
            'foto'
        ]


# -------------------------
# PROPIETARIO (CREA TODO JUNTO)
# -------------------------
class PropietarioCompletoForm(forms.ModelForm):

    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Propietario
        fields = [
            'nombre',
            'apellido',
            'telefono',
            'tipo_documento',
            'documento',
            'ciudad',
            'direccion',
            'foto'
        ]

    # ✅ VALIDACIÓN DE CORREO
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado")
        return correo

    # ✅ VALIDACIÓN DE DOCUMENTO
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if Propietario.objects.filter(documento=documento).exists():
            raise forms.ValidationError("Este documento ya está registrado")
        return documento

    # ✅ VALIDACIÓN DE TELÉFONO (CORREGIDO)
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')  # ❌ antes estaba mal (documento)

        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números")

        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos")

        if Propietario.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Este teléfono ya está registrado")

        return telefono

    # ✅ VALIDACIÓN DE NOMBRE
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if len(nombre) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("Solo se permiten letras")

        return nombre.upper() 
    
    # ✅ VALIDACIÓN DE APELLIDO
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio")

        if len(apellido) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError("Solo se permiten letras")

        return apellido.upper() 




    # ✅ SAVE CORREGIDO
    def save(self, commit=True):
        with transaction.atomic():

            usuario = Usuario(
                correo=self.cleaned_data['correo'],
                rol=Usuario.Rol.PROPIETARIO,
                estado=Usuario.Estado.ACTIVO
            )
            usuario.password = make_password(self.cleaned_data['password'])

            if commit:
                usuario.save()

            propietario = super().save(commit=False)
            propietario.usuario = usuario

            if commit:
                propietario.save()

            return propietario
#------------------------------------
class PropietarioUpdateForm(forms.ModelForm):

    correo = forms.EmailField()

    class Meta:
        model = Propietario
        fields = [
            'nombre',
            'apellido',
            'telefono',
            'ciudad',
            'direccion',
            'foto'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.usuario:
            self.fields['correo'].initial = self.instance.usuario.correo

    # 🔹 CORREO
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')

        if Usuario.objects.filter(correo=correo)\
                .exclude(id=self.instance.usuario.id)\
                .exists():
            raise forms.ValidationError("Este correo ya está registrado")

        return correo

    # 🔹 NOMBRE
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if len(nombre) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("Solo se permiten letras")

        return nombre.upper()  # 👈 mayúscula automática

    # 🔹 APELLIDO
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio")

        if len(apellido) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError("Solo se permiten letras")

        return apellido.upper()

    # 🔹 TELÉFONO
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números")

        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos")

        if Propietario.objects.filter(telefono=telefono)\
                .exclude(id=self.instance.id)\
                .exists():
            raise forms.ValidationError("Este teléfono ya está registrado")

        return telefono
    
    # 🔹 CIUDAD
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')

        if not ciudad:
            raise forms.ValidationError("La ciudad es obligatoria")

        if len(ciudad) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        return ciudad.title()

    # 🔹 DIRECCIÓN
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')

        if not direccion:
            raise forms.ValidationError("La dirección es obligatoria")

        if len(direccion) < 5:
            raise forms.ValidationError("La dirección es muy corta")

        return direccion

    # 🔹 FOTO (opcional)
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')

        if foto:
            if foto.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("La imagen no debe superar 2MB")

        return foto

    # 🔹 SAVE
    def save(self, commit=True):
        with transaction.atomic():

            propietario = super().save(commit=False)
            usuario = propietario.usuario

            usuario.correo = self.cleaned_data['correo']

            if self.cleaned_data.get('password'):
                usuario.password = make_password(self.cleaned_data['password'])

            if commit:
                usuario.save()
                propietario.save()

            return propietario
#-------------------------------------


# ---------------------------------------------------------------------------------------------
# VETERINARIO
# ---------------------------------------------------------------------------------------------

# -------CREAR------------------------

class VeterinarioCompletoForm(forms.ModelForm):

    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    dias_laborales = forms.MultipleChoiceField(
        choices=[
            ('lunes', 'Lunes'),
            ('martes', 'Martes'),
            ('miercoles', 'Miércoles'),
            ('jueves', 'Jueves'),
            ('viernes', 'Viernes'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo'),
        ],
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Veterinario
        fields = [
            'nombre',
            'apellido',
            'telefono',
            'tipo_documento',
            'documento',
            'especialidad',
            'servicios',
            'num_licencia',
            'horario_inicio',
            'horario_fin',
            'dias_laborales',
            'foto'
        ]
        widgets = {
            'especialidad': forms.Select(attrs={'id': 'id_especialidad'}),
            'servicios': forms.SelectMultiple(attrs={'id': 'id_servicios'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    # ---------------- VALIDACIONES ----------------

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("El nombre solo puede contener letras")

        return nombre.upper()

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio")

        if len(apellido) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError("Solo se permiten letras")

        return apellido.upper()

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números")

        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos")

        if Veterinario.objects.filter(telefono=telefono)\
                .exclude(id=self.instance.id)\
                .exists():
            raise forms.ValidationError("Este teléfono ya está registrado")

        return telefono
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')

        if not documento:
            raise forms.ValidationError("El documento es obligatorio")

        if not documento.isdigit():
            raise forms.ValidationError(
                "El documento solo debe contener números"
            )

        if len(documento) < 6:
            raise forms.ValidationError(
                "El documento es demasiado corto"
            )

        if Veterinario.objects.filter(documento=documento).exists():
            raise forms.ValidationError(
                "Este documento ya está registrado"
            )

        return documento
    
    def clean_num_licencia(self):
        licencia = self.cleaned_data.get('num_licencia')

        if not licencia:
            raise forms.ValidationError("La licencia es obligatoria")

        if not re.match(r'^[A-Za-z0-9\-]{5,20}$', licencia):
            raise forms.ValidationError(
            "Formato inválido. Ej: MVZ-12345 o 12345")

        return licencia
    

   
    def clean_dias_laborales(self):
        dias = self.cleaned_data.get('dias_laborales')

        if not dias:
            raise forms.ValidationError("Debes seleccionar al menos un día")

        dias_validos = [
            'lunes', 'martes', 'miercoles',
            'jueves', 'viernes', 'sabado', 'domingo'
        ]

        for dia in dias:
            if dia.lower() not in dias_validos:
                raise forms.ValidationError(f"Día inválido: {dia}")

        return dias
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            raise forms.ValidationError("La contraseña es obligatoria")

        if len(password) < 6:
            raise forms.ValidationError("La contraseña debe tener mínimo 6 caracteres")

        if len(password) > 8:
            raise forms.ValidationError("La contraseña debe tener máximo 8 caracteres")

        return password

    # ---------------- VALIDACIÓN GENERAL ----------------

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('horario_inicio')
        fin = cleaned_data.get('horario_fin')

        if inicio and fin:
            if inicio >= fin:
                raise forms.ValidationError(
                    "La hora de inicio debe ser menor que la hora de fin."
                )

        return cleaned_data

    # ---------------- INIT ----------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['servicios'].queryset = Servicio.objects.none()

        if 'especialidad' in self.data:
            try:
                especialidad_id = int(self.data.get('especialidad'))
                self.fields['servicios'].queryset = Servicio.objects.filter(
                    especialista_required_id=especialidad_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.especialidad:
            self.fields['servicios'].queryset = Servicio.objects.filter(
                especialista_required=self.instance.especialidad
            )

    # ---------------- SAVE ----------------

    def save(self, commit=True):
        with transaction.atomic():

            usuario = Usuario.objects.create(
                correo=self.cleaned_data['correo'],
                rol=Usuario.Rol.VETERINARIO,
                estado=Usuario.Estado.ACTIVO,
                password=make_password(self.cleaned_data['password'])
            )

            veterinario = super().save(commit=False)
            veterinario.usuario = usuario

            if commit:
                veterinario.save()
                self.save_m2m()

            return veterinario
#-------------ACTUALIZAR--------------------------------------------
class VeterinarioUpdateForm(forms.ModelForm):

    correo = forms.EmailField()

    # ❌ ESTADO YA NO SE PIDE EN EL FORM (solo correo)
    # estado se maneja en la vista o save()

    dias_laborales = forms.MultipleChoiceField(
        choices=[
            ('lunes', 'Lunes'),
            ('martes', 'Martes'),
            ('miercoles', 'Miércoles'),
            ('jueves', 'Jueves'),
            ('viernes', 'Viernes'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False  # 🔥 IMPORTANTE
    )

    class Meta:
        model = Veterinario
        fields = [
            'nombre', 'apellido','telefono',
            'tipo_documento','documento','especialidad', 'servicios',
            'num_licencia', 'horario_inicio', 'horario_fin',
            'dias_laborales', 'foto'
        ]

    # ---------------- INIT ----------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Usuario actual
        if self.instance and self.instance.usuario:
            self.fields['correo'].initial = self.instance.usuario.correo

        # días laborales iniciales
        if self.instance:
            self.fields['dias_laborales'].initial = self.instance.dias_laborales

        # filtro servicios dinámico
        self.fields['servicios'].queryset = Servicio.objects.none()

        if 'especialidad' in self.data:
            try:
                especialidad_id = int(self.data.get('especialidad'))
                self.fields['servicios'].queryset = Servicio.objects.filter(
                    especialista_required_id=especialidad_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.especialidad:
            self.fields['servicios'].queryset = Servicio.objects.filter(
                especialista_required=self.instance.especialidad
            )
    # ---------------- VALIDACIONES ----------------

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError("El nombre solo puede contener letras")

        return nombre.upper()

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio")

        if len(apellido) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError("Solo se permiten letras")

        return apellido.upper()

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números")

        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos")

        if Veterinario.objects.filter(telefono=telefono)\
                .exclude(id=self.instance.id)\
                .exists():
            raise forms.ValidationError("Este teléfono ya está registrado")

        return telefono
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')

        if not documento:
            raise forms.ValidationError(
                "El documento es obligatorio"
            )

        if not documento.isdigit():
            raise forms.ValidationError(
                "El documento solo debe contener números"
            )

        if Veterinario.objects.filter(documento=documento)\
                .exclude(id=self.instance.id)\
                .exists():

            raise forms.ValidationError(
                "Este documento ya está registrado"
            )

        return documento

    def clean_num_licencia(self):
        licencia = self.cleaned_data.get('num_licencia')

        if not licencia:
            raise forms.ValidationError("La licencia es obligatoria")

        if len(licencia) < 5:
            raise forms.ValidationError("El número de licencia es demasiado corto")

        return licencia

    def clean_dias_laborales(self):
        dias = self.cleaned_data.get('dias_laborales')

        if not dias:
            raise forms.ValidationError("Debes seleccionar al menos un día")

        dias_validos = [
            'lunes', 'martes', 'miercoles',
            'jueves', 'viernes', 'sabado', 'domingo'
        ]

        for dia in dias:
            if dia.lower() not in dias_validos:
                raise forms.ValidationError(f"Día inválido: {dia}")

        return dias

    # ---------------- VALIDACIÓN GENERAL ----------------

    def clean(self):
        cleaned_data = super().clean()

        inicio = cleaned_data.get('horario_inicio')
        fin = cleaned_data.get('horario_fin')

        if inicio and fin:
            if inicio >= fin:
                raise forms.ValidationError(
                    "La hora de inicio debe ser menor que la hora de fin."
                )

        return cleaned_data
    
from django.contrib.auth.hashers import make_password, check_password

class CambiarPasswordForm(forms.Form):

    password_actual = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput
    )

    nueva_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput
    )

    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput
    )

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_password_actual(self):
        password_actual = self.cleaned_data.get('password_actual')

        if not check_password(password_actual, self.usuario.password):
            raise forms.ValidationError("La contraseña actual es incorrecta")

        return password_actual

    def clean(self):
        cleaned_data = super().clean()

        nueva = cleaned_data.get('nueva_password')
        confirmar = cleaned_data.get('confirmar_password')

        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError(
                "Las contraseñas no coinciden"
            )

        if nueva:
            if len(nueva) < 6:
                raise forms.ValidationError(
                    "La nueva contraseña debe tener mínimo 6 caracteres"
                )

            if len(nueva) > 8:
                raise forms.ValidationError(
                    "La nueva contraseña debe tener máximo 8 caracteres"
                )

        return cleaned_data

    def save(self):
        self.usuario.password = make_password(
            self.cleaned_data['nueva_password']
        )

        self.usuario.fecha_cambio_password = timezone.now()

        self.usuario.save()

        return self.usuario

class CsvUploadForm(forms.Form):

    csv_file = forms.FileField(
        label="Archivo CSV",
        help_text="Debe contener columnas válidas"
    )