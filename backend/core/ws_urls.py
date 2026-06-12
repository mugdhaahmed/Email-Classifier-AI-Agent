from django.urls import path
from agent import consumers

# Standard Django path works natively inside Channels URLRouter instances!
websocket_urlpatterns = [
    path('ws/emails/', consumers.EmailConsumer.as_asgi()),  # type: ignore
]