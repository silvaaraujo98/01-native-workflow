"""ASGI config for the weekly feedback project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weekly_feedback.settings")

application = get_asgi_application()
