"""
ASGI config for kameleon_back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter

from django.core.asgi import get_asgi_application, URLRouter
from channels.auth import AuthMiddlewareStack
from routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kameleon_back.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
