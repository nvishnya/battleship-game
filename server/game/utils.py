from channels.db import database_sync_to_async
# from game.serializers import GameSerializer
from game.models import Game, Player
from twisted.protocols.memcache import ClientError
from game.serializers import GameSerializer, YouSerializer


@database_sync_to_async
def create_player(channel_name):
    return Player.objects.create(channel_name=channel_name)


@database_sync_to_async
def delete_player(player_id):
    Player.objects.get(id=player_id).delete()

@database_sync_to_async
def get_player_data(player_id):
    player = Player.objects.get(id=player_id)
    return YouSerializer(player).data

@database_sync_to_async
def place_ships(player_id, rows, cols, ships):
    player = Player.objects.get(id=player_id)
    return player.create_board_and_place_ships(rows, cols, ships)


@database_sync_to_async
def create_game(rows, cols, playerA_id, playerB_id=None):
    playerA = Player.objects.get(id=playerA_id)
    if playerB_id is None:
        return Game.create(rows, cols, playerA)
    playerB = Player.objects.get(id=playerB_id)
    return Game.create(rows, cols, playerA, playerB)


@database_sync_to_async
def add_player_to_game(game, player_id):
    player = Player.objects.get(id=player_id)
    return game.add_player_to_game(player)


@database_sync_to_async
def get_random_available_player(player_id):
    player = Player.objects.get(id=player_id)
    return Player.get_random_available_player(player)


@database_sync_to_async
def get_game_data(game_id, player_id):
    game = Game.objects.get(id=game_id)
    player = Player.objects.get(id=player_id)
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
def game_shoot(game_id, player_id, x, y):
    game = Game.objects.get(id=game_id)
    player = Player.objects.get(id=player_id)
    game.shoot(player, x, y)
