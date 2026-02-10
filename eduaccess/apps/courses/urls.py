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

    # dashboard docente accesibilidad (opcional)
    path(
        "<int:offering_id>/accessibility/",
        views.accessibility_dashboard,
        name="accessibility_dashboard"
    ),
    path(
        "<int:offering_id>/module/<int:module_id>/complete/",
        views.complete_module,
        name="complete_module"
),

]
