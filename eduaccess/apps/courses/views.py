from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CourseOffering, Module, ModuleProgress, Content  # Importamos Content
from django.utils import timezone


# DASHBOARD DOCENTE DE ACCESIBILIDAD
@login_required
def accessibility_dashboard(request, offering_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)
    modules = offering.modules.all()

    return render(request, "courses/accessibility_dashboard.html", {
        "offering": offering,
        "modules": modules
    })


# REDIRECCIÓN AL PRIMER MÓDULO DEL CURSO
@login_required
def course_detail(request, offering_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)

    first_module = offering.modules.order_by("order").first()

    if first_module:
        return redirect(
            "course_module_detail",
            offering_id=offering.id,
            module_id=first_module.id
        )

    return redirect("student_home")


# VISTA PRINCIPAL DEL CURSO (MÓDULO ACTIVO)
@login_required
def course_module_detail(request, offering_id, module_id):
    offering = get_object_or_404(
        CourseOffering.objects.select_related("course"),
        id=offering_id
    )

    # Sidebar → todos los módulos del curso
    modules = offering.modules.all().order_by("order")

    # Módulo activo
    # Agregamos prefetch_related('contents') para traer los videos/textos de forma eficiente
    active_module = get_object_or_404(
        Module.objects.prefetch_related("materials", "contents"),
        id=module_id,
        offering=offering
    )

    # Obtenemos los materiales antiguos y los nuevos contenidos mezclados
    materials = active_module.materials.all()
    contents = active_module.contents.all().order_by("order")  # Los nuevos elementos multimedia

    # 🔥 CREAR O ACTUALIZAR PROGRESO DEL MÓDULO
    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=active_module,
        defaults={
            "completed": False,
            "last_accessed": timezone.now(),
        }
    )

    # Si ya existía, actualizar última visita
    if not created:
        progress.last_accessed = timezone.now()
        progress.save(update_fields=["last_accessed"])

    context = {
        "offering": offering,
        "course": offering.course,
        "modules": modules,
        "active_module": active_module,
        "materials": materials,
        "contents": contents,  # Nueva variable para el template
        "progress": progress,
    }

    return render(request, "courses/course_player.html", context)


@login_required
def complete_module(request, offering_id, module_id):
    module = get_object_or_404(Module, id=module_id, offering_id=offering_id)

    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=module
    )

    progress.completed = True
    progress.last_accessed = timezone.now()
    progress.save()

    # Intentar ir al siguiente módulo si existe
    next_module = Module.objects.filter(
        offering_id=offering_id,
        order__gt=module.order
    ).order_by('order').first()

    if next_module:
        return redirect("course_module_detail", offering_id=offering_id, module_id=next_module.id)

    return redirect("course_module_detail", offering_id=offering_id, module_id=module_id)