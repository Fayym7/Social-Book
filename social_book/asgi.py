"""
ASGI config for social_book project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

#the next three lines should be always in the upper portion of the entire code
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_book.settings')
django_asgi_app = get_asgi_application()

import asyncc.routing
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack


application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket':AuthMiddlewareStack(
    URLRouter(
        asyncc.routing.websocket_urlpatterns
    ))
})