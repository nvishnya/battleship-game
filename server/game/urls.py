from django.urls.conf import path
from game.views import get_random_board, new_game

urlpatterns = [
    path('random-board/', get_random_board),
    path('new-game/', new_game)
]