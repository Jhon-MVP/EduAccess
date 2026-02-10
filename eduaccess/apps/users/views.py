from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from .models import UserProfile
from accessibility.models import AccessibilityProfile


# =========================================================
# LOGIN PERSONALIZADO + ONBOARDING ACCESIBILIDAD
# =========================================================
class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        selected_role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)
        error = None

        if user is None:
            error = "Usuario o contraseña incorrectos."
            return render(request, self.template_name, {"error": error})

        # Verificar que tenga perfil
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            error = "Este usuario no tiene un perfil asignado."
            return render(request, self.template_name, {"error": error})

        # Validar rol seleccionado
        if profile.role != selected_role:
            error = f"El usuario no puede iniciar sesión como {selected_role.lower()}."
            return render(request, self.template_name, {"error": error})

        # LOGIN OK
        login(request, user)

        # =====================================================
        # 🔥 NUEVO FLUJO LIMPIO
        # =====================================================

        # 👨‍🎓 ESTUDIANTE
        if profile.role == UserProfile.Role.STUDENT:

            # ¿Tiene perfil de accesibilidad?
            has_accessibility_profile = AccessibilityProfile.objects.filter(
                user=user
            ).exists()

            # Primera vez → onboarding accesibilidad
            if not has_accessibility_profile:
                return redirect("select_accessibility")

            # Usuario normal → dashboard
            return redirect("student_home")

        # 👨‍🏫 DOCENTE
        elif profile.role == UserProfile.Role.TEACHER:
            return redirect("teacher_home")

        # 👑 ADMIN
        else:
            return redirect("admin:index")


# =========================================================
# (LEGACY) GUARDAR CONFIG ACCESIBILIDAD ANTIGUA
# =========================================================
@login_required
def save_accessibility_settings(request):
    if request.method == "POST":
        profile = UserProfile.objects.get(user=request.user)
        profile.visual = 'visual' in request.POST
        profile.hearing = 'hearing' in request.POST
        profile.other = 'other' in request.POST
        profile.save()

        if profile.role == UserProfile.Role.STUDENT:
            return redirect("student_home")
        elif profile.role == UserProfile.Role.TEACHER:
            return redirect("teacher_home")

    return redirect("student_home")


# =========================================================
# PERFIL DEL ESTUDIANTE (VER + EDITAR + ACCESIBILIDAD)
# =========================================================
@login_required
def student_profile(request):

    user = request.user

    # Siempre debe existir
    accessibility_profile, _ = AccessibilityProfile.objects.get_or_create(user=user)

    # detectar modo edición
    edit_mode = request.GET.get("edit") == "1"

    # -----------------------------------------------------
    # GUARDAR CAMBIOS DEL PERFIL + ACCESIBILIDAD
    # -----------------------------------------------------
    if request.method == "POST":

        # datos básicos del usuario
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        # accesibilidad
        disability_type = request.POST.get("disability_type")
        accessibility_profile.disability_type = disability_type or None

        accessibility_profile.high_contrast = request.POST.get("high_contrast") == "on"
        accessibility_profile.subtitles = request.POST.get("subtitles") == "on"

        font_size = request.POST.get("font_size")
        if font_size:
            accessibility_profile.font_size = int(font_size)

        accessibility_profile.save()

        # volver al modo vista
        return redirect("student_profile")

    context = {
        "user_obj": user,
        "accessibility_profile": accessibility_profile,
        "edit_mode": edit_mode,
    }

    return render(request, "users/student_profile.html", context)
