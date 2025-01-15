"""
ASGI config for kameleon_back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kameleon_back.settings')
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from django.urls import path
from back.consumers import ChatConsumer, NotificationConsumer, CoopConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/", ChatConsumer.as_asgi()),
            path("ws/notifications/", NotificationConsumer.as_asgi()),
            path("ws/coop/<int:riddle_id>/", CoopConsumer.as_asgi()),
        ])
    ),
})
