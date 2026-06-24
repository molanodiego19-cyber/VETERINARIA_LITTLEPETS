from django.urls import path
from . import views

urlpatterns = [
    path("run-scheduler/", views.run_scheduler, name="run_scheduler"),
    path("test-email/", views.test_email, name="test_email"),
    path("smtp-info/", views.smtp_info, name="smtp_info"),

]
