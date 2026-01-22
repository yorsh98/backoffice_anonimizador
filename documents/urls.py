from django.urls import path

from .views import (
    DocumentDetailView,
    DocumentDownloadView,
    DocumentListView,
    DocumentUploadView,
)

app_name = "documents"

urlpatterns = [
    path("", DocumentListView.as_view(), name="list"),
    path("upload/", DocumentUploadView.as_view(), name="upload"),
    path("<uuid:document_id>/", DocumentDetailView.as_view(), name="detail"),
    path("<uuid:document_id>/download/", DocumentDownloadView.as_view(), name="download"),
]
