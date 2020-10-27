from game.models import Board, Ship, Coordinate, Game, Player
import numpy as np
import pytest
from django.forms.models import model_to_dict


@pytest.fixture
def player_factory(db):
    def create_player(channel):
        return Player.create(channel)
    return create_player


# board


@pytest.fixture
def board_factory(db):
    def create_board(player, rows=10, cols=10,):
        return Board.create(player, rows, cols)
    return create_board


@pytest.fixture
def board10x10(db, board_factory, player_factory):
    return board_factory(player_factory('channel'))


@pytest.fixture
def ship_factory(db, board10x10):
    def create_ship(x, y, rows, cols):
        ship = Ship.objects.create(x=x, y=y, rows=rows, cols=cols, board=board10x10)
        Ship.add_coordinates(ship)
        return ship
    return create_ship


@pytest.fixture
def ship1x4_at0x0(db, ship_factory):
    return ship_factory(0, 0, 1, 4)


@pytest.fixture
def ship2x1_at4x4(db, ship_factory):
    return ship_factory(4, 4, 2, 1)


array10x10_empty = np.zeros((10, 10), dtype=np.int8)
array10x10_1x1_at4x4 = array10x10_empty.copy()
array10x10_1x1_at4x4[4:5, 4:5] = 1


ship1x3_at4x4_data = {'x': 4, 'y': 4, 'rows': 1, 'cols': 3}
ship1x1_at0x0_data = {'x': 0, 'y': 0, 'rows': 1, 'cols': 1}
ship_invalid = {'x': -1, 'y': 0, 'rows': 1, 'cols': 1}


@pytest.mark.parametrize("array, x, y, rows, cols, expected", [
    (array10x10_empty, 0, 0, 3, 1, True),
    (array10x10_empty, 6, 6, 3, 1, True),

    (array10x10_empty, 0, 9, 1, 3, False),
    (array10x10_empty, 9, 0, 3, 1, False),

    (array10x10_1x1_at4x4, 4, 4, 1, 1, False),
    (array10x10_1x1_at4x4, 5, 5, 1, 1, False),
    (array10x10_1x1_at4x4, 5, 5, 1, 2, False),

    (array10x10_1x1_at4x4, 6, 6, 1, 1, True),
])
def test_board_is_placement_possible_boundaries(db, array, x, y, rows, cols, expected):
    assert Board.is_placement_possible(array, x, y, rows, cols) == expected


def test_board_add_ships_to_db(db, board10x10):
    assert Ship.objects.filter(board=board10x10).count() == 0
    ship = board10x10.add_ships_to_db(ship1x3_at4x4_data)[0]
    assert Ship.objects.filter(board=board10x10).count() == 1
    assert ship.coordinate_set.all().count() == 3


def test_board_ships_alive(db, board10x10):
    board10x10.add_ships_to_db(ship1x3_at4x4_data)
    assert board10x10.ships_alive == 1
    board10x10.add_ships_to_db(ship1x1_at0x0_data)
    assert board10x10.ships_alive == 2


def test_board_all_ships_are_shot(db, board10x10):
    ship = board10x10.add_ships_to_db(ship1x3_at4x4_data)[0]
    assert not board10x10.all_ships_are_shot
    ship.coordinate_set.all().update(is_hit=True)
    assert board10x10.all_ships_are_shot


def test_board_mark_surrounding_cells(db, board10x10):
    board10x10.place_ships(ship1x1_at0x0_data)
    ship = board10x10.ship_set.all()[0]
    marked = Board._mark_surrounding_cells(board10x10.shots, model_to_dict(ship))
    assert marked[marked == Board.MISS].size == 3


def test_board_shots_with_marked(db, board10x10):
    #     marks surrounding cells only for sunken ships
    board10x10.place_ships(ship1x3_at4x4_data)
    ship = board10x10.ship_set.all()[0]
    assert board10x10.shots_with_marked[board10x10.shots_with_marked == Board.MISS].size == 0
    ship.coordinate_set.all().update(is_hit=True)
    assert board10x10.shots_with_marked[board10x10.shots_with_marked == Board.MISS].size == 12


def test_board_place_ships(db, board10x10):
    assert board10x10.place_ships(ship1x1_at0x0_data)
    assert not board10x10.place_ships(ship_invalid)


def test_board_shoot(db, board10x10):
    board10x10.place_ships(ship1x1_at0x0_data)
    assert not board10x10.shoot(1, 1)
    assert board10x10.shoot(0, 0)
    assert board10x10.shots[0, 0] == 2
    assert Coordinate.objects.get(x=0, y=0, ship__board=board10x10).is_hit


@pytest.mark.parametrize("rows, cols, expected", [
    (10, 10, 4),
    (10, 15, 4),
    (15, 15, 5),
    (20, 15, 5),
    (20, 20, 6),
])
def test_board_get_number_of_ships_per_player(db, rows, cols, expected):
    assert Board.get_number_of_ships_per_player(rows, cols) == expected


def test_board_generate_initial_board(db, board10x10):
    ships_data = Board.generate_initial_board(10, 10)
    assert board10x10.place_ships(*ships_data)


# ship


def test_ship_length(db, ship1x4_at0x0, ship2x1_at4x4):
    assert ship1x4_at0x0.length == 4
    assert ship2x1_at4x4.length == 2


def test_ship_orientation(db, ship1x4_at0x0, ship2x1_at4x4):
    assert ship1x4_at0x0.orientation == 'HR'
    assert ship2x1_at4x4.orientation == 'VR'


def test_ship_parts_left(db, ship2x1_at4x4):
    assert ship2x1_at4x4.parts_left == 2
    coordinates = ship2x1_at4x4.coordinate_set.all()
    coordinates[0].hit()
    assert ship2x1_at4x4.parts_left == 1


def test_ship_is_alive(db, ship2x1_at4x4):
    assert ship2x1_at4x4.is_alive
    coordinates = ship2x1_at4x4.coordinate_set.all()
    for coordinate in coordinates:
        coordinate.hit()
    assert not ship2x1_at4x4.is_alive


def test_ship_indicies(db, ship2x1_at4x4):
    assert ship2x1_at4x4.indicies == (slice(4, 6), slice(4, 5))


def test_ship_generate_random_ship(db):
    rows, cols = Ship.generate_random_ship(length=3).values()
    assert (rows == 3 and cols == 1) or (rows == 1 and cols == 3)


# game


@pytest.fixture
def game_factory(db):
    def create_game(player, rows, cols):
        return Game.create(player, rows, cols)
    return create_game


@pytest.fixture
def gameA(db, player_factory, game_factory):
    return game_factory(player_factory('playerA'), 10, 10)


@pytest.fixture
def gameAB(db, game_factory, player_factory):
    game = game_factory(player_factory('channelA'), 10, 10)
    game.join(player_factory('channelB'))
    return game


def test_game_join_game(db, player_factory, gameA):
    player = player_factory('channel')
    gameA.join(player)
    assert gameA.playerB == player


def test_game_next_player(db, gameAB):
    assert gameAB.current == gameAB.playerA
    gameAB.next_player()
    assert gameAB.current == gameAB.playerB


def test_game_shoot(db, gameAB):
    gameAB.playerB.board.place_ships(ship1x1_at0x0_data)
    gameAB.playerA.board.place_ships(ship1x1_at0x0_data)

    assert gameAB.current == gameAB.playerA
    gameAB.shoot(gameAB.playerB, 0, 0)
    assert gameAB.current == gameAB.playerA
    gameAB.shoot(gameAB.playerA, 1, 1)
    assert gameAB.current == gameAB.playerB
    gameAB.shoot(gameAB.playerB, 0, 0)
    assert gameAB.current == gameAB.playerB
