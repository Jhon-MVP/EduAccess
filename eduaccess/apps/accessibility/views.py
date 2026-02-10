from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .models import AccessibilityProfile
from users.models import UserProfile


@login_required
def select_accessibility(request):

    profile = get_object_or_404(UserProfile, user=request.user)

    # Redirección según rol
    if profile.role == UserProfile.Role.STUDENT:
        redirect_url = "student_home"
    elif profile.role == UserProfile.Role.TEACHER:
        redirect_url = "teacher_home"
    else:
        redirect_url = "logout"

    # Obtener o crear perfil accesibilidad
    accessibility, _ = AccessibilityProfile.objects.get_or_create(user=request.user)

    # =====================================================
    # 🟢 GUARDAR CONFIGURACIÓN DEL MODAL
    # =====================================================
    if request.method == "POST":

        disability_type = request.POST.get("disability_type")

        # Guardar tipo principal
        accessibility.disability_type = disability_type or None

        # 🔵 RESET TOTAL (evita combinaciones inválidas)
        accessibility.high_contrast = False
        accessibility.subtitles = False
        accessibility.font_size = 3  # default

        # ==============================
        # VISUAL
        # ==============================
        if disability_type == "VISUAL":
            accessibility.high_contrast = request.POST.get("high_contrast") == "on"

            font_size = request.POST.get("font_size")
            if font_size:
                accessibility.font_size = int(font_size)

        # ==============================
        # AUDITIVA
        # ==============================
        elif disability_type == "AUDITIVA":
            accessibility.subtitles = request.POST.get("subtitles") == "on"

        # Si eligió NINGUNA → todo queda en default

        accessibility.save()

        return redirect(redirect_url)

    return render(
        request,
        "accessibility/select_accessibility.html",
        {"accessibility": accessibility},
    )
