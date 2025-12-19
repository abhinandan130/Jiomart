"""
WSGI config for jiomart_clone project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from .session_startup import clear_all_sessions

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jiomart_clone.settings')

application = get_wsgi_application()


clear_all_sessions()  # Delete all sessions when server restarts