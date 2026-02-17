from django.urls import re_path
from .consumers import PollConsumer

websocket_urlpatterns = [
    re_path(r"ws/poll/(?P<slug>[^/]+)/$", PollConsumer.as_asgi()),
]