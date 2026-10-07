"""اجرای نسخه لینک (FastAPI) از manage.py."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'اجرای API نسخه لینک روی پورت 8100'

    def add_arguments(self, parser):
        parser.add_argument('--host', default='127.0.0.1')
        parser.add_argument('--port', default=8100, type=int)

    def handle(self, *args, **options):
        import uvicorn
        self.stdout.write(self.style.SUCCESS(
            f"نسخه لینک: http://{options['host']}:{options['port']}/docs"
        ))
        uvicorn.run(
            'chatbot.link_api.app:app',
            host=options['host'],
            port=options['port'],
            reload=False,
        )
