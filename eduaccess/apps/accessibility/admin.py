from django.contrib import admin
from .models import AccessibilityProfile


@admin.register(AccessibilityProfile)
class AccessibilityProfileAdmin(admin.ModelAdmin):
    """
    Panel de administración para perfiles de accesibilidad
    """
    list_display = (
        "user",
        "disability_type",
        "high_contrast",
        "font_size",
        "subtitles",
        "updated_at",
    )

    list_filter = (
        "disability_type",
        "high_contrast",
        "subtitles",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Usuario", {
            "fields": ("user",)
        }),
        ("Configuración de Discapacidad", {
            "fields": ("disability_type",),
            "description": "Selecciona el tipo de discapacidad para habilitar opciones específicas"
        }),
        ("Opciones Visuales", {
            "fields": ("high_contrast", "font_size"),
            "description": "Configuración para usuarios con discapacidad visual"
        }),
        ("Opciones Auditivas", {
            "fields": ("subtitles",),
            "description": "Configuración para usuarios con discapacidad auditiva"
        }),
        ("Información del Sistema", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    list_per_page = 25
    ordering = ("-updated_at",)
