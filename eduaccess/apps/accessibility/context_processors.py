from .models import AccessibilityProfile

def accessibility_settings(request):
    """
    Hace disponibles las preferencias de accesibilidad
    en TODOS los templates automáticamente.
    """

    if not request.user.is_authenticated:
        return {}

    profile, _ = AccessibilityProfile.objects.get_or_create(user=request.user)

    return {
        "accessibility": profile
    }
