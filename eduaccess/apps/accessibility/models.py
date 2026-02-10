from django.conf import settings
from django.db import models


class AccessibilityProfile(models.Model):
    """
    Perfil de accesibilidad del usuario.
    Almacena todas las preferencias de accesibilidad personalizadas.
    """

    class DisabilityType(models.TextChoices):
        VISUAL = "VISUAL", "Discapacidad visual"
        AUDITIVA = "AUDITIVA", "Discapacidad auditiva"
        NINGUNA = "NINGUNA", "Ninguna"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accessibility_profile'
    )

    # Tipo principal de discapacidad (opcional)
    disability_type = models.CharField(
        max_length=20,
        choices=DisabilityType.choices,
        blank=True,
        null=True,
        verbose_name="Tipo de Discapacidad"
    )

    # Opciones Visual
    high_contrast = models.BooleanField(
        default=False,
        verbose_name="Alto Contraste"
    )

    font_size = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Tamaño de Fuente",
        help_text="De 1 (muy pequeño) a 5 (muy grande)"
    )

    # Opciones Auditiva
    subtitles = models.BooleanField(
        default=True,
        verbose_name="Subtítulos Automáticos"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Accesibilidad"
        verbose_name_plural = "Perfiles de Accesibilidad"

    def __str__(self):
        disability = self.get_disability_type_display() if self.disability_type else "Sin configurar"
        return f"{self.user.username} - {disability}"

    def get_font_size_display_name(self):
        """Retorna el nombre legible del tamaño de fuente"""
        sizes = {
            1: "Muy pequeño",
            2: "Pequeño",
            3: "Normal",
            4: "Grande",
            5: "Muy grande"
        }
        return sizes.get(self.font_size, "Normal")
