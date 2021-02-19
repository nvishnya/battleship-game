from game.models import Game, Player
from channels.db import database_sync_to_async
from game.serializers import GameSerializer, YouSerializer


def get_game_and_player(game_id, player_id):
    game = Game.objects.get(id=game_id)
    player = Player.objects.get(id=player_id)
    return game, player


@database_sync_to_async
def can_game_be_joined(game_id):
    temp = Game.objects.filter(id=game_id)
    if temp.count() != 0:
        return True
    return False


@database_sync_to_async
def create_player(channel_name):
    return Player.objects.create(channel_name=channel_name)


@database_sync_to_async
def place_ships(player_id, ships, rows=10, cols=10):
    player = Player.objects.get(id=player_id)
    return player.create_board_and_place_ships(ships, rows, cols)


@database_sync_to_async
def create_new_game(playerA_id, playerB_id=None, rows=10, cols=10):
    playerA = Player.objects.get(id=playerA_id)
    if playerB_id is None:
        return Game.create(playerA, None, rows, cols)
    playerB = Player.objects.get(id=playerB_id)
    return Game.create(playerA, playerB, rows, cols)


@database_sync_to_async
def add_player_to_game(game_id, player_id):
    game, player = get_game_and_player(game_id, player_id)
    return game.add_player_to_game(player)


@database_sync_to_async
def get_game_data(game_id, player_id):
    game, player = get_game_and_player(game_id, player_id)
    return GameSerializer(game, context={"player": player}).data


@database_sync_to_async
def get_player_data(player_id):
    player = Player.objects.get(id=player_id)
    return YouSerializer(player).data


@database_sync_to_async
def get_random_opponent(player_id):
    player = Player.objects.get(id=player_id)
    return Player.get_random_available_player(player)


@database_sync_to_async
def shoot_at(x, y, game_id, player_id):
    game, player = get_game_and_player(game_id, player_id)
    game.shoot(player, x, y)


@database_sync_to_async
def delete_player(player_id):
    Player.objects.get(id=player_id).delete()


@database_sync_to_async
def leave_game(player_id, game_id=None):
    Player.objects.get(id=player_id).leave_game(game_id)
