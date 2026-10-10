from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0003_site_content_flags"),
    ]

    operations = [
        migrations.CreateModel(
            name="KnowledgeChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_type", models.CharField(max_length=32, verbose_name="نوع منبع")),
                ("source_key", models.CharField(max_length=80, verbose_name="کلید منبع")),
                ("source_label", models.CharField(blank=True, max_length=255, verbose_name="نام منبع")),
                ("text", models.TextField(verbose_name="متن")),
                ("embedding", models.JSONField(default=list, verbose_name="بردار")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chunks",
                        to="chatbot.chatbotprofile",
                        verbose_name="پروفایل",
                    ),
                ),
            ],
            options={
                "verbose_name": "قطعهٔ دانش",
                "verbose_name_plural": "قطعه‌های دانش RAG",
            },
        ),
        migrations.AddIndex(
            model_name="knowledgechunk",
            index=models.Index(fields=["profile", "source_type"], name="chatbot_chunk_type_idx"),
        ),
        migrations.AddIndex(
            model_name="knowledgechunk",
            index=models.Index(fields=["profile", "source_key"], name="chatbot_chunk_key_idx"),
        ),
    ]
