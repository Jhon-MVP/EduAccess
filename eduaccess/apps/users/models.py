from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Estudiante"
        TEACHER = "TEACHER", "Docente"
        ADMIN = "ADMIN", "Administrador"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    # ⭐ NUEVO — FOTO DE PERFIL
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
