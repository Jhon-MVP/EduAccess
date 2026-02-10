from django.conf import settings
from django.db import models


class AccessibilityProfile(models.Model):
    class DisabilityType(models.TextChoices):
        VISUAL = "VISUAL", "Discapacidad visual"
        AUDITIVA = "AUDITIVA", "Discapacidad auditiva"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Tipo principal de discapacidad (opcional)
    disability_type = models.CharField(
        max_length=20,
        choices=DisabilityType.choices,
        blank=True,
        null=True
    )

    # Opciones Visual
    high_contrast = models.BooleanField(default=False)
    font_size = models.PositiveSmallIntegerField(default=3)  # 1 a 5

    # Opciones Auditiva
    subtitles = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.disability_type or 'Ninguna'}"
