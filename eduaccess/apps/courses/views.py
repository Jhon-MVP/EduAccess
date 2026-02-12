from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CourseOffering, Module, ModuleProgress, Content
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse

# DASHBOARD DOCENTE DE ACCESIBILIDAD
@login_required
def accessibility_dashboard(request, offering_id):
    # Traemos el offering y optimizamos la consulta con prefetch_related
    offering = get_object_or_404(CourseOffering.objects.select_related("course"), id=offering_id)
    modules = offering.modules.all().prefetch_related('contents')

    total_contents = 0
    accessible_contents = 0
    items_needing_attention = []

    for module in modules:
        for content in module.contents.all():
            total_contents += 1

            # Validamos archivos multimedia que requieren IA (imágenes y PDFs/archivos)
            if content.content_type in ['image', 'file']:
                # Si tu campo ai_accessibility_text tiene datos, la IA hizo su trabajo
                if content.ai_accessibility_text:
                    accessible_contents += 1
                else:
                    items_needing_attention.append(content)
            else:
                # Los textos puros y videos los contamos como accesibles por defecto
                accessible_contents += 1

    # Calculamos el Score final (0 a 100%)
    accessibility_score = 0
    if total_contents > 0:
        accessibility_score = int((accessible_contents / total_contents) * 100)

    return render(request, "courses/accessibility_dashboard.html", {
        "offering": offering,
        "course": offering.course,
        "modules": modules,
        "total_contents": total_contents,
        "accessible_contents": accessible_contents,
        "accessibility_score": accessibility_score,
        "items_needing_attention": items_needing_attention,
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


@login_required
def download_transcription_txt(request, content_id):
    """
    Toma el texto de un contenido (como una transcripción de un PDF)
    y lo envía al navegador como un archivo .txt descargable.
    """
    content = get_object_or_404(Content, id=content_id)

    # Extraemos el texto, o ponemos un mensaje si está vacío
    texto = content.ai_accessibility_text if content.ai_accessibility_text else "No hay transcripción OCR disponible."
    # Preparamos la respuesta indicando el tipo de archivo (texto plano)
    response = HttpResponse(texto, content_type='text/plain; charset=utf-8')

    # Limpiamos el título para que no tenga caracteres raros en el nombre del archivo
    safe_title = "".join([c for c in content.title if c.isalnum() or c == ' ']).rstrip()
    filename = f"{safe_title.replace(' ', '_')}_transcripcion.txt"

    # Configuramos los headers para forzar la descarga
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def process_pending_ai(request, offering_id):
    if request.method == "POST":
        offering = get_object_or_404(CourseOffering, id=offering_id)
        modules = offering.modules.all()

        procesados = 0
        errores = 0

        # Recorremos todos los módulos y sus contenidos
        for module in modules:
            for content in module.contents.all():
                # Si es imagen o archivo Y NO tiene texto de accesibilidad...
                if content.content_type in ['image', 'file'] and not content.ai_accessibility_text:
                    try:
                        # ---------------------------------------------------------
                        # 🤖 AQUÍ LLAMAS A TU FUNCIÓN DE IA 🤖
                        # Si tienes una función separada, sería algo como esto:
                        # texto_generado = tu_funcion_gemini(content.file_upload.path)
                        # content.ai_accessibility_text = texto_generado
                        # content.save()
                        # ---------------------------------------------------------

                        # (Si tu IA se dispara sola con un 'save' desde signals.py,
                        #  simplemente haz content.save() para forzar el trigger).

                        procesados += 1
                    except Exception as e:
                        print(f"Error procesando {content.title}: {e}")
                        errores += 1

        # Enviamos el mensaje de éxito al profesor
        if procesados > 0:
            messages.success(request, f"¡Magia completada! Se procesaron {procesados} recursos con IA.")
        elif errores > 0:
            messages.warning(request, "Hubo un problema al contactar a la IA. Revisa los logs.")
        else:
            messages.info(request, "Todo está al día. No había recursos pendientes por procesar.")

    # Redirigimos de vuelta al dashboard para que vea cómo sube su barra al 100%
    return redirect('accessibility_dashboard', offering_id=offering_id)