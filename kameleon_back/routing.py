from django.urls import path
from back.consumers import RiddleConsumer

websocket_urlpatterns = [
    path('ws/riddles/<int:riddle_id>/', RiddleConsumer.as_asgi(), name='riddle-consumer'),
]
