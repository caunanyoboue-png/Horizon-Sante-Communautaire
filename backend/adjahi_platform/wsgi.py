"""Configuration WSGI pour le projet."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adjahi_platform.settings")

application = get_wsgi_application()
