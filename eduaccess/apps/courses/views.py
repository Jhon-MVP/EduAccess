from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CourseOffering, Module, ModuleProgress, Content  # Importamos Content
from django.utils import timezone
from django.contrib import messages

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


# apps/courses/views.py
# (Reemplaza la función add_content_to_module con esta)

@login_required
def upload_course_content(request, offering_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)
    # Ordenamos los módulos para que salgan en orden 1, 2, 3...
    modules = offering.modules.all().order_by('order')

    if request.method == "POST":
        action = request.POST.get("action")

        # ACCIÓN 1: EL PROFESOR CREA UN NUEVO MÓDULO
        if action == "create_module":
            title = request.POST.get("module_title")
            description = request.POST.get("module_description", "")

            # Calculamos automáticamente el orden (si hay 2, este será el 3)
            last_module = modules.last()
            next_order = (last_module.order + 1) if last_module else 1

            Module.objects.create(
                offering=offering,
                title=title,
                description=description,
                order=next_order
            )
            messages.success(request, f"¡Módulo '{title}' creado exitosamente!")
            return redirect("upload_course_content", offering_id=offering.id)

        # ACCIÓN 2: EL PROFESOR SUBE CONTENIDO A UN MÓDULO EXISTENTE
        elif action == "upload_content":
            module_id = request.POST.get("module_id")
            module = get_object_or_404(Module, id=module_id, offering=offering)

            title = request.POST.get("title")
            content_type = request.POST.get("content_type")
            text_content = request.POST.get("text_content", "")
            video_url = request.POST.get("video_url", "")
            file_upload = request.FILES.get("file_upload")

            last_content = module.contents.order_by('order').last()
            next_order = (last_content.order + 1) if last_content else 1

            Content.objects.create(
                module=module,
                title=title,
                content_type=content_type,
                text_content=text_content,
                video_url=video_url,
                file_upload=file_upload,
                order=next_order
            )

            messages.success(request, f"El recurso '{title}' se subió y la IA lo está procesando.")
            return redirect("upload_course_content", offering_id=offering.id)

    return render(request, "courses/upload_content.html", {
        "offering": offering,
        "modules": modules
    })


# apps/courses/views.py (Pega esto al final)

@login_required
def edit_content(request, offering_id, content_id):
    offering = get_object_or_404(CourseOffering, id=offering_id)
    # Buscamos el contenido asegurando que pertenece a este curso
    content = get_object_or_404(Content, id=content_id, module__offering=offering)

    if request.method == "POST":
        content.title = request.POST.get("title")

        # Actualizamos la información dependiendo de qué tipo de recurso sea
        if content.content_type == 'text':
            content.text_content = request.POST.get("text_content", "")
        elif content.content_type == 'video':
            content.video_url = request.POST.get("video_url", "")
        elif content.content_type in ['image', 'file']:
            # Solo actualizamos el archivo si el profesor seleccionó uno nuevo
            if request.FILES.get("file_upload"):
                content.file_upload = request.FILES.get("file_upload")
                # Nota: Tu archivo signals.py detectará el cambio y llamará a la IA automáticamente

        content.save()
        messages.success(request, f"¡Recurso '{content.title}' actualizado correctamente!")
        return redirect("upload_course_content", offering_id=offering.id)

    return render(request, "courses/edit_content.html", {
        "offering": offering,
        "content": content
    })


@login_required
def delete_content(request, offering_id, content_id):
    content = get_object_or_404(Content, id=content_id, module__offering_id=offering_id)
    if request.method == "POST":
        content.delete()
        messages.success(request, "Recurso eliminado del curso.")
    return redirect("upload_course_content", offering_id=offering_id)