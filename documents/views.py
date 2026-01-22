from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.generic import DetailView, FormView, ListView, View

from .forms import DocumentUploadForm
from .models import Document


def is_admin(user: User) -> bool:
    return user.groups.filter(name="ADMIN").exists()


def is_funcionario(user: User) -> bool:
    return user.groups.filter(name="FUNCIONARIO").exists()


class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return is_admin(user) or is_funcionario(user)


class DocumentListView(GroupRequiredMixin, ListView):
    model = Document
    template_name = "documents/list.html"
    context_object_name = "documents"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not is_admin(user):
            queryset = queryset.filter(uploaded_by=user)

        status = self.request.GET.get("status")
        name = self.request.GET.get("name")
        date_from = parse_date(self.request.GET.get("date_from", ""))
        date_to = parse_date(self.request.GET.get("date_to", ""))
        user_id = self.request.GET.get("user")

        if status:
            queryset = queryset.filter(status=status)
        if name:
            queryset = queryset.filter(original_filename__icontains=name)
        if date_from:
            queryset = queryset.filter(uploaded_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(uploaded_at__date__lte=date_to)
        if user_id and is_admin(user):
            queryset = queryset.filter(uploaded_by_id=user_id)

        return queryset

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = is_admin(self.request.user)
        context["users"] = User.objects.all() if context["is_admin"] else []
        context["filters"] = self.request.GET
        return context


class DocumentDetailView(GroupRequiredMixin, DetailView):
    model = Document
    template_name = "documents/detail.html"
    context_object_name = "document"
    pk_url_kwarg = "document_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_admin(self.request.user):
            return queryset
        return queryset.filter(uploaded_by=self.request.user)


class DocumentUploadView(GroupRequiredMixin, FormView):
    form_class = DocumentUploadForm
    template_name = "documents/upload.html"
    document: Document | None = None

    def form_valid(self, form):
        document = form.save(commit=False)
        document.uploaded_by = self.request.user
        document.save()
        self.document = document
        return super().form_valid(form)

    def get_success_url(self):
        if not self.document:
            raise RuntimeError("Document was not saved before redirect.")
        return reverse("documents:detail", kwargs={"document_id": self.document.id})


class DocumentDownloadView(GroupRequiredMixin, View):
    def get(self, request, document_id):
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist as exc:
            raise Http404 from exc

        if not is_admin(request.user) and document.uploaded_by_id != request.user.id:
            raise PermissionDenied

        file_handle = document.file.open("rb")
        response = FileResponse(file_handle, content_type=document.content_type)
        response["Content-Disposition"] = f'attachment; filename="{document.original_filename}"'
        return response
