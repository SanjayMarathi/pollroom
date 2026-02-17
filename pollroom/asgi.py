import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import polls.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pollroom.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(polls.routing.websocket_urlpatterns)
    ),
})