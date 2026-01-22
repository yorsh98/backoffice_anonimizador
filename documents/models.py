from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone


class DocumentStatus(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded"
    PROCESSING = "processing", "Processing"
    READY = "ready", "Ready"
    ERROR = "error", "Error"


def document_upload_path(instance: "Document", filename: str) -> str:
    uploaded_at = instance.uploaded_at or timezone.now()
    date_path = uploaded_at.strftime("%Y/%m")
    safe_name = Path(filename).name
    return f"documents/{date_path}/{instance.id}/{safe_name}"


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.UPLOADED,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.original_filename} ({self.id})"
