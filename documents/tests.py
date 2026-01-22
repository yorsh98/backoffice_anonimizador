import io

import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from documents.models import Document


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(username="admin", password="pass")
    admin_group = Group.objects.get(name="ADMIN")
    user.groups.add(admin_group)
    return user


@pytest.fixture
def funcionario_user(db):
    user = User.objects.create_user(username="func", password="pass")
    func_group = Group.objects.get(name="FUNCIONARIO")
    user.groups.add(func_group)
    return user


@pytest.fixture
def other_funcionario(db):
    user = User.objects.create_user(username="other", password="pass")
    func_group = Group.objects.get(name="FUNCIONARIO")
    user.groups.add(func_group)
    return user


@pytest.fixture
def sample_document(db, funcionario_user):
    content = io.BytesIO(b"dummy content")
    uploaded_file = SimpleUploadedFile(
        "test.pdf",
        content.read(),
        content_type="application/pdf",
    )
    document = Document.objects.create(
        file=uploaded_file,
        original_filename="test.pdf",
        content_type="application/pdf",
        size_bytes=uploaded_file.size,
        sha256="deadbeef",
        uploaded_by=funcionario_user,
    )
    return document


@pytest.mark.django_db
def test_login_required(client):
    response = client.get(reverse("documents:list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_funcionario_cannot_view_others_document(client, other_funcionario, sample_document):
    client.login(username="other", password="pass")
    response = client.get(reverse("documents:detail", args=[sample_document.id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_admin_can_view_document(client, admin_user, sample_document):
    client.login(username="admin", password="pass")
    response = client.get(reverse("documents:detail", args=[sample_document.id]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_upload_valid_document(client, funcionario_user):
    client.login(username="func", password="pass")
    upload = SimpleUploadedFile("file.pdf", b"data", content_type="application/pdf")
    response = client.post(reverse("documents:upload"), {"file": upload})
    assert response.status_code == 302
    assert Document.objects.filter(original_filename="file.pdf").exists()


@pytest.mark.django_db
def test_upload_invalid_extension(client, funcionario_user):
    client.login(username="func", password="pass")
    upload = SimpleUploadedFile("file.txt", b"data", content_type="text/plain")
    response = client.post(reverse("documents:upload"), {"file": upload})
    assert response.status_code == 200
    assert "Solo se permiten archivos PDF o DOCX." in response.content.decode()
