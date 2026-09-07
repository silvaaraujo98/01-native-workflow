"""WSGI config for the weekly feedback project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weekly_feedback.settings")

application = get_wsgi_application()
