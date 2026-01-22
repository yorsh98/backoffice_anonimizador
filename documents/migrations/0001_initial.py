from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import documents.models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True, default=uuid.uuid4, editable=False, serialize=False
                    ),
                ),
                ("file", models.FileField(upload_to=documents.models.document_upload_path)),
                ("original_filename", models.CharField(max_length=255)),
                ("content_type", models.CharField(max_length=100)),
                ("size_bytes", models.PositiveIntegerField()),
                ("sha256", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("uploaded", "Uploaded"),
                            ("processing", "Processing"),
                            ("ready", "Ready"),
                            ("error", "Error"),
                        ],
                        default="uploaded",
                        max_length=20,
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
    ]
