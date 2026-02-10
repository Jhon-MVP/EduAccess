from django.urls import path
from .views import CustomLoginView, save_accessibility_settings, student_profile

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("save-accessibility/", save_accessibility_settings, name="save_accessibility_settings"),

    # ⭐ NUEVA RUTA PERFIL
    path("profile/", student_profile, name="student_profile"),
]
