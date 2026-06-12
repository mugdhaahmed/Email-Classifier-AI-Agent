import os
import django
from django.core.asgi import get_asgi_application

# 1. Initialize standard Django settings configuration environment context first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 2. Safely import Channels routing tools AFTER django.setup() to avoid registry crashes
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core import ws_urls  # Import the module namespace cleanly

application = ProtocolTypeRouter({
    # Routes standard REST/HTTP queries
    "http": get_asgi_application(),
    
    # Routes persistent live socket handshakes
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ws_urls.websocket_urlpatterns  # Point directly to the inner array property
        )
    ),
})