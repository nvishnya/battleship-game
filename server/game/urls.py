from django.urls.conf import path
from game.views import get_random_board, GameView

urlpatterns = [
    path('random-board/', get_random_board),
    path('game/<int:pk>/', GameView.as_view())
]