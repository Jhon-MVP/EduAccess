# apps/courses/apps.py
from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'  # <--- QUITA el "apps." aquí

    def ready(self):
        import courses.signals  # <--- Importación corta