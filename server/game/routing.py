from django.urls.conf import path
from game import consumers


websocket_urlpatterns = [
    path('ws/', consumers.GameConsumer.as_asgi()),
]
