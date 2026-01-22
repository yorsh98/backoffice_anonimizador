from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "original_filename",
        "status",
        "uploaded_by",
        "uploaded_at",
        "size_bytes",
    )
    list_filter = ("status", "uploaded_at")
    search_fields = ("original_filename", "uploaded_by__username", "sha256")
    readonly_fields = (
        "original_filename",
        "content_type",
        "size_bytes",
        "sha256",
        "uploaded_at",
        "updated_at",
    )
