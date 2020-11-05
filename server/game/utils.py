from channels.db import database_sync_to_async
# from game.serializers import GameSerializer
from game.models import Game, Player
from twisted.protocols.memcache import ClientError
from game.serializers import GameSerializer

@database_sync_to_async
def create_player(channel_name):
    return Player.objects.create(channel_name=channel_name)


@database_sync_to_async
def delete_player(player):
    player.delete()


@database_sync_to_async
def place_ships(player, rows, cols, ships):
    return player.create_board_and_place_ships(rows, cols, ships)


@database_sync_to_async
def create_game(rows, cols, playerA, playerB):
    return Game.create(rows, cols, playerA, playerB)


@database_sync_to_async
def add_player_to_game(game, player):
    return game.add_player_to_game(player)


@database_sync_to_async
def get_random_available_player(player):
    return Player.get_random_available_player(player)


@database_sync_to_async
def get_game_data(game_id, player):
    game = Game.objects.get(id=game_id)
    return GameSerializer(game, context={"player": player}).data


@database_sync_to_async
def is_playerB_none(game_id):
    return Game.objects.get(id=game_id).playerB is None


@database_sync_to_async
def get_game(game_id):
    return Game.objects.get(pk=game_id)


@database_sync_to_async
def get_game_or_error(game_id):
    try:
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        raise ClientError("INVALID_GAME")
    return game

@database_sync_to_async
def game_shoot(game_id, player, x, y):
    game = Game.objects.get(id=game_id)
    game.shoot(player, x, y)
