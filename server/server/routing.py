from channels.routing import ProtocolTypeRouter, URLRouter
import game.routing

application = ProtocolTypeRouter({
    "websocket": URLRouter(game.routing.websocket_urlpatterns)
})
