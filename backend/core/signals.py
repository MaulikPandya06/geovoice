from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Statement
from core.services.embedding_service import embed_statement
from core.tasks import regenerate_summary_task


@receiver(post_save, sender=Statement)
def auto_embed_on_save(sender, instance, created, **kwargs):
    """
    Automatically chunk and embed a Statement whenever it is created.
    Only runs on creation — not on every save (to avoid re-embedding on field updates).
    """
    if created:
        embed_statement(instance)

        regenerate_summary_task.apply_async(
            args=[instance.country.id, instance.event.id],
            countdown=10
        )
