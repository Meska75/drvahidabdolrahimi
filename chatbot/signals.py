"""ذخیرهٔ محتوای سایت، RAG پروفایل‌هایی را که تیک خودکار دارند به‌روز می‌کند."""

import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save

logger = logging.getLogger('chatbot')


def _profiles_for(source):
    from chatbot.models import ChatbotProfile
    if not source:
        return []
    return list(ChatbotProfile.objects.filter(
        sync_site_auto=True,
        **{f'sync_site_{source}': True},
    ))


def _item_key(instance):
    return {
        'FaqItem': f'faq-{instance.pk}',
        'ServiceItem': f'service-{instance.pk}',
        'DoctorEducation': f'education-{instance.pk}',
        'DoctorAchievement': f'achievement-{instance.pk}',
        'DoctorClinic': f'clinic-{instance.pk}',
        'TeamMember': f'team-{instance.pk}',
        'Post': f'post-{instance.pk}',
    }.get(instance.__class__.__name__, '')


def _apply(instance):
    from chatbot.services.site_index import source_type_of, sync_instance
    source = source_type_of(instance)
    for profile in _profiles_for(source):
        try:
            err = sync_instance(profile, instance)
            if err:
                logger.warning('RAG سایت به‌روز نشد: %s', err)
        except Exception:
            logger.exception('به‌روزرسانی خودکار RAG ناموفق')


def _on_save(sender, instance, **kwargs):
    if kwargs.get('raw'):
        return
    transaction.on_commit(lambda: _apply(instance))


def _on_delete(sender, instance, **kwargs):
    from chatbot.services.site_index import remove_item, source_type_of
    source = source_type_of(instance)
    key = _item_key(instance)

    def run():
        for profile in _profiles_for(source):
            try:
                remove_item(profile, key)
            except Exception:
                logger.exception('حذف خودکار از RAG ناموفق')

    transaction.on_commit(run)


def connect_site_signals():
    from blog.models import Post
    from main.models import DoctorAchievement, DoctorClinic, DoctorEducation, FaqItem
    from services.models import ServiceItem
    from team.models import TeamMember

    for model in (
        FaqItem, DoctorEducation, DoctorAchievement, DoctorClinic,
        ServiceItem, TeamMember, Post,
    ):
        label = model._meta.label
        post_save.connect(_on_save, sender=model, dispatch_uid=f'chatbot-rag-save-{label}')
        post_delete.connect(_on_delete, sender=model, dispatch_uid=f'chatbot-rag-del-{label}')
