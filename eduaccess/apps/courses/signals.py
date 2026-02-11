from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction  # <--- Importante
from .services.accessibility import process_content_with_ia


@receiver(post_save, sender='courses.Content')
def auto_process_ai_content(sender, instance, created, **kwargs):
    if created and instance.file_upload and not instance.is_processed_by_ia:
        # ⭐ LA MAGIA ESTÁ AQUÍ:
        # Esto ejecuta la IA después de que la base de datos se haya desbloqueado
        transaction.on_commit(lambda: execute_ai_processing(instance.pk))


def execute_ai_processing(content_id):
    """
    Función auxiliar para procesar la IA fuera de la transacción principal.
    """
    from courses.models import Content
    try:
        instance = Content.objects.get(pk=content_id)
        result = process_content_with_ia(instance)

        if result:
            instance.ai_accessibility_text = result
            instance.is_processed_by_ia = True
            instance.save(update_fields=['ai_accessibility_text', 'is_processed_by_ia'])
    except Content.DoesNotExist:
        pass