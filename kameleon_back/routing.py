from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/riddles/(?P<riddle_id>\d+)/$', consumers.RiddleConsumer.as_asgi()),
]
