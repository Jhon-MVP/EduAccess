from django.urls import path
from . import views

urlpatterns = [
    # entrar al curso → redirige al primer módulo
    path("<int:offering_id>/", views.course_detail, name="course_detail"),

    # ver módulo específico
    path(
        "<int:offering_id>/module/<int:module_id>/",
        views.course_module_detail,
        name="course_module_detail"
    ),

    # dashboard docente accesibilidad
    path(
        "<int:offering_id>/accessibility/",
        views.accessibility_dashboard,
        name="accessibility_dashboard"
    ),

    # completar modulo
    path(
        "<int:offering_id>/module/<int:module_id>/complete/",
        views.complete_module,
        name="complete_module"
    ),

    # NUEVA RUTA: Para la página de subir material (Reemplaza a la vieja)
    path(
        "<int:offering_id>/upload/",
        views.upload_course_content,
        name="upload_course_content"
    ),

    path("<int:offering_id>/content/<int:content_id>/edit/", views.edit_content, name="edit_content"),
    path("<int:offering_id>/content/<int:content_id>/delete/", views.delete_content, name="delete_content"),
    path('content/<int:content_id>/download-txt/', views.download_transcription_txt, name='download_transcription_txt'),
    path('<int:offering_id>/accessibility/process-ai/', views.process_pending_ai, name='process_pending_ai'),
]