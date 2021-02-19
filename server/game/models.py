from django.core.validators import MinValueValidator, MaxValueValidator
from picklefield.fields import PickledObjectField
from django.forms.models import model_to_dict
from builtins import staticmethod
from django.db import models
from scipy import signal
import numpy as np


def delete_if_exists(model, attribute, value):
    queryset = model.objects.filter(**{attribute: value})
    if queryset.count() != 0:
        queryset[0].delete()
        return True
    return False


class Player(models.Model):
    channel_name = models.CharField(max_length=125)
    is_busy = models.BooleanField(default=False)

    def leave_game(self, game_id=None):
        self.set_busy(False)
        delete_if_exists(Board, 'player', self)
        delete_if_exists(Game, 'id', game_id)

    @staticmethod
    def create(channel_name):
        return Player.objects.create(channel_name=channel_name)

    @staticmethod
    def update_players_statuses(*players):
        for player in players:
            if player is None:
                continue
            player.set_busy()

    @staticmethod
    def get_random_available_player(player):
        available = Player.objects.filter(is_busy=False, board__isnull=False).exclude(id=player.id)
        if available.count() == 0:
            return None
        else:
            index = np.random.randint(0, available.count())
            return available[index]

    def set_busy(self, is_busy=True):
        self.is_busy = is_busy
        self.save(update_fields=['is_busy'])

    def create_board_and_place_ships(self, ships, rows, cols):
        board = Board.create(self, rows, cols)
        return board.place_ships(*ships)


class Board(models.Model):
    player = models.OneToOneField(Player, on_delete=models.deletion.CASCADE)

    MAX_SIZE = 20
    MIN_SIZE = 5

    MISS = 1
    HIT = 2

    board = PickledObjectField()
    shots = PickledObjectField()

    @property
    def shots_with_marked(self):
        data = [model_to_dict(ship) for ship in self.ship_set.all() if not ship.is_alive]
        return Board._mark_surrounding_cells(self.shots, *data)

    def shoot(self, x, y):
        if self.board[x, y] > 0:
            self.shots[x, y] = Board.HIT
            self.board[x, y] = -1
            coordinate = Coordinate.objects.get(x=x, y=y, ship__board=self)
            coordinate.hit()
            self.save(update_fields=['shots', 'board'])
            return True
        else:
            self.shots[x, y] = Board.MISS
            self.save(update_fields=['shots'])
            return False

    @staticmethod
    def create(player, rows, cols):
        board = np.zeros((rows, cols), dtype=np.int8)
        shots = np.zeros((rows, cols), dtype=np.int8)
        return Board.objects.create(player=player, board=board, shots=shots)

    @staticmethod
    def get_number_of_ships_per_player(rows, cols):
        # rows or cols > 5!
        size = np.min([rows, cols])
        return np.int8(np.floor(size - (6 + 4 * (size / 5 - 2))))

    @staticmethod
    def get_ships_lengths(rows, cols):
        biggest = Board.get_number_of_ships_per_player(rows, cols)
        temp = np.arange(1, biggest + 1, 1)
        lengths = np.concatenate([np.full((i), j) for i, j in zip(temp, temp[::-1])])
        return lengths

    @staticmethod
    def generate_initial_board(rows, cols):
        ships_lengths = Board.get_ships_lengths(rows, cols)
        board = np.zeros((rows, cols), dtype=np.int8)
        possible_coordinates = np.argwhere(board < 1)
        ships = []

        for length in ships_lengths:
            rows, cols = Ship.generate_random_ship(length).values()
            ind = np.random.choice(possible_coordinates.shape[0])
            x, y = possible_coordinates[ind]

            while not Board.is_placement_possible(board, x, y, rows, cols):
                possible_coordinates = np.delete(possible_coordinates, ind, axis=0)
                ind = np.random.choice(possible_coordinates.shape[0])
                x, y = possible_coordinates[ind]

            data = {"rows": rows, "cols": cols, "x": x, "y": y}
            board[Ship._get_indicies(data)] = 1
            ships.append(data)
            possible_coordinates = np.argwhere(Board._mark_surrounding_cells(board, data) < 1)

        return ships

    @staticmethod
    def is_placement_possible(board, x, y, rows, cols):
        kernel = np.ones((3, 3), dtype=np.int8)
        neighbours = signal.convolve(board, kernel, mode="same")
        z = neighbours[x: x + rows, y: y + cols]
        return True if (z.sum() == 0 and z.shape == (rows, cols)) else False

    @property
    def ships_alive(self):
        return len([x for x in self.ship_set.all() if x.is_alive])

    @property
    def all_ships_are_shot(self):
        return self.ships_alive == 0

    def add_ships_to_db(self, *ships):
        present_ids = list(Ship.objects.filter(board=self).values_list('id', flat=True))
        Ship.objects.bulk_create([Ship(board=self, **ship) for ship in ships])
        new_ships = Ship.objects.filter(board=self).exclude(id__in=present_ids)

        Ship.add_coordinates(*new_ships)
        return new_ships

    def add_ships_on_board(self, ships):
        for ship in ships:
            self.board[ship.indicies] = ship.length
        self.save(update_fields=['board'])

    def place_ships(self, *ships):
        ships = [{k: v for k, v in ship.items() if k not in ['length', 'orientation']}
                 for ship in ships]
        for ship in ships:
            if not Board.is_placement_possible(self.board, **ship):
                return False  # could not place one of the ships; discard all

        ships = self.add_ships_to_db(*ships)
        self.add_ships_on_board(ships)
        return True  # all ships were placed successfully

    @staticmethod
    def _mark_surrounding_cells(array, *data):
        new_array = array.copy()
        for ship in data:
            new_array[Ship._get_indicies(ship, offset=True)] = Board.MISS
            new_array[Ship._get_indicies(ship)] = array[Ship._get_indicies(ship)]
        return new_array

    def is_already_shot(self, x, y):
        return self.shots[x, y] > 0


class Game(models.Model):
    rows = models.IntegerField(validators=[MinValueValidator(
        Board.MIN_SIZE), MaxValueValidator(Board.MAX_SIZE)])
    cols = models.IntegerField(validators=[MinValueValidator(
        Board.MIN_SIZE), MaxValueValidator(Board.MAX_SIZE)])

    is_over = models.BooleanField(default=False)
    winner = models.ForeignKey('Player', on_delete=models.deletion.CASCADE,
                               related_name="winner", null=True, blank=True)
    current = models.ForeignKey('Player', on_delete=models.deletion.CASCADE,
                                related_name="current", null=True, blank=True)
    playerA = models.ForeignKey('Player', on_delete=models.deletion.CASCADE,
                                related_name="playerA", null=True, blank=True)
    playerB = models.ForeignKey('Player', on_delete=models.deletion.CASCADE,
                                related_name="playerB", null=True, blank=True)

    @staticmethod
    def create(playerA, playerB=None, rows=10, cols=10):
        game = Game.objects.create(rows=rows,
                                   cols=cols,
                                   playerA=playerA,
                                   playerB=playerB,
                                   current=playerA)

        Player.update_players_statuses(playerA, playerB)
        return game

    def end_game(self):
        self.is_over = True
        self.save(update_fields=['is_over'])

    def add_player_to_game(self, player):
        if self.playerA is None:
            self.playerA = player
            self.current = player
        elif self.playerB is None:
            self.playerB = player
        else:
            return False

        self.save(update_fields=['playerA', 'playerB', 'current'])
        Player.update_players_statuses(player)
        return True

    def next_player(self):
        self.current = self.playerA if self.current != self.playerA else self.playerB
        self.save(force_update=True)

# x, y boundaries
    def shoot(self, player, x, y):
        opponent = self.playerA if self.current == self.playerB else self.playerB
        if player != self.current or opponent.board.is_already_shot(x, y):
            return
        hit = opponent.board.shoot(x, y)
        if hit:
            self.is_over = True if opponent.board.ships_alive == 0 else False
            self.winner = self.current if self.is_over else None
            self.save(update_fields=['is_over', 'winner'])
        else:
            self.next_player()
#         return hit


class Ship(models.Model):
    board = models.ForeignKey(Board, on_delete=models.deletion.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    rows = models.IntegerField()
    cols = models.IntegerField()

    @property
    def is_alive(self):
        return self.parts_left != 0

    @property
    def orientation(self):
        return 'VR' if self.rows > self.cols else 'HR'

    @property
    def length(self):
        return int(np.maximum(self.rows, self.cols))

    @property
    def parts_left(self):
        return self.coordinate_set.all().filter(is_hit=False).count()

    @property
    def indicies(self):
        return Ship._get_indicies(model_to_dict(self))

    @staticmethod
    def _get_indicies(data, offset=False, max=10):

        def _min(n): return 0 if n < 0 else n
        def _max(n): return max if n > n else n

        i = int(offset)
        s = np.s_[_min(data['x'] - i): _max(data['x'] + data['rows'] + i),
                  _min(data['y'] - i): _max(data['y'] + data['cols'] + i)]
        return s

    @staticmethod
    def generate_random_ship(length):
        keys = ["rows", "cols"]
        vals = np.random.choice([1, length], size=2, replace=False)
        return dict(zip(keys, vals))

    @staticmethod
    def add_coordinates(*ships):
        coordinates = []
        for ship in ships:
            for row in range(ship.rows):
                for col in range(ship.cols):
                    coordinates.append(Coordinate(ship=ship, x=ship.x+row, y=ship.y+col))

        Coordinate.objects.bulk_create(coordinates)


class Coordinate(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    is_hit = models.BooleanField(default=False)
    ship = models.ForeignKey(Ship, on_delete=models.deletion.CASCADE)

    def hit(self):
        self.is_hit = True
        self.save(update_fields=['is_hit'])
