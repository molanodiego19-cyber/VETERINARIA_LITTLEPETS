from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("citas.urls")),
    path("panel/", include("panel.urls")),
    path("citas/", include("citas.urls")),
    path("veterinario/", include("veterinarioapp.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("facturacion/", include("facturacion.urls")),
    path("notificacion/", include("notificacion.urls")),
    path("mascota/", include("mascota.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
