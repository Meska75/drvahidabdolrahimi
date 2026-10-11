from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    verbose_name = 'چت‌بات هوش مصنوعی'

    def ready(self):
        import mimetypes
        mimetypes.add_type('application/wasm', '.wasm')
        mimetypes.add_type('application/zip', '.lottie')
        from chatbot.signals import connect_site_signals
        connect_site_signals()
