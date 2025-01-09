from django.urls import re_path
from back.consumers import RiddleConsumer

websocket_urlpatterns = [
    re_path(r'ws/riddles/(?P<riddle_id>\d+)/$', RiddleConsumer.as_asgi()),
]
