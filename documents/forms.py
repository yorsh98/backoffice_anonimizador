from __future__ import annotations

import hashlib
from pathlib import Path

from django import forms
from django.conf import settings

from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file"]

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        extension = Path(uploaded_file.name).suffix.lower()
        if extension not in settings.DOCUMENT_ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Solo se permiten archivos PDF o DOCX.")
        if uploaded_file.size > settings.DOCUMENT_MAX_UPLOAD_SIZE:
            raise forms.ValidationError("El archivo supera el tamaño máximo permitido.")
        return uploaded_file

    def save(self, commit: bool = True):
        document = super().save(commit=False)
        uploaded_file = self.cleaned_data["file"]
        document.original_filename = uploaded_file.name
        document.content_type = uploaded_file.content_type or "application/octet-stream"
        document.size_bytes = uploaded_file.size
        document.sha256 = self._calculate_sha256(uploaded_file)
        if commit:
            document.save()
        return document

    @staticmethod
    def _calculate_sha256(uploaded_file) -> str:
        hasher = hashlib.sha256()
        for chunk in uploaded_file.chunks():
            hasher.update(chunk)
        uploaded_file.seek(0)
        return hasher.hexdigest()
