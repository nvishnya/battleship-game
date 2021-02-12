from django.urls.conf import path
from game.views import get_random_board

urlpatterns = [
    path('random-board/', get_random_board),
]