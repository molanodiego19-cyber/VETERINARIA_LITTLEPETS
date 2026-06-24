from django.urls import path
from . import views

urlpatterns = [
    path("smtp-test/", views.smtp_test, name="smtp_test"),
    path("smtp-info/", views.smtp_info, name="smtp_info"),
    path("test-email/", views.test_email, name="test_email"),
    path("run-scheduler/", views.run_scheduler, name="run_scheduler"),
]