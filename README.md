# Backoffice Anonimizador

Proyecto Django para backoffice interno con login y módulo de documentos.

## Requisitos

- Python 3.12
- Postgres (recomendado en producción)

## Instalación (desarrollo)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Producción

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py collectstatic

gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Estructura

- `config/`: configuración del proyecto (settings, urls, wsgi)
- `accounts/`: login/logout y grupos
- `documents/`: modelo y vistas de documentos
- `templates/`: templates HTML

## Roles

- `ADMIN`: acceso a todos los documentos.
- `FUNCIONARIO`: solo documentos propios.

## Tests

```bash
pytest
```
