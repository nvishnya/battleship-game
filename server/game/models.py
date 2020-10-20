from django.core.validators import MinValueValidator, MaxValueValidator
from picklefield.fields import PickledObjectField
from django.forms.models import model_to_dict
from builtins import staticmethod
from django.db import models
from scipy import signal
import numpy as np


class Player(models.Model):
    username = models.CharField(max_length=25, unique=True)
    board = models.ForeignKey('Board', on_delete=models.deletion.CASCADE)

    @staticmethod
    def create(username, rows, cols):
        board = Board.create(rows, cols)
        return Player.objects.create(username=username, board=board)


class Board(models.Model):
    MAX_SIZE = 20
    MIN_SIZE = 5

    board = PickledObjectField()
    shots = PickledObjectField()

    def shoot(self, x, y):
        self.shots[x, y] = True
        if self.board[x, y] > 0:
            self.board[x, y] = -1
            coordinate = Coordinate.objects.get(x=x, y=y, ship__board=self)
            coordinate.hit()
            self.save(update_fields=['shots', 'board'])
            if not coordinate.ship.is_alive:
                self.mark_surrounding_cells(coordinate.ship)
            return True
        else:
            self.save(update_fields=['shots'])
            return False

    @staticmethod
    def create(rows, cols):
        board = np.zeros((rows, cols), dtype=np.int8)
        shots = np.zeros((rows, cols), dtype=np.bool8)
        return Board.objects.create(board=board, shots=shots)

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

    def add_ships_to_db(self, *xyships):
        present_ids = list(Ship.objects.filter(board=self).values_list('id', flat=True))
        Ship.objects.bulk_create([Ship(board=self, **xyship) for xyship in xyships])
        new_ships = Ship.objects.filter(board=self).exclude(id__in=present_ids)

        Ship.add_coordinates(*new_ships)
        return new_ships

    def add_ships_on_board(self, ships):
        for ship in ships:
            self.board[ship.indicies] = ship.length
        self.save(update_fields=['board'])

    def place_ships(self, *xyships):
        for xyship in xyships:
            if not Board.is_placement_possible(self.board, **xyship):
                return False  # could not place one of the ships; discard all

        ships = self.add_ships_to_db(*xyships)
        self.add_ships_on_board(ships)
        return True  # all ships were placed successfully

    def mark_surrounding_cells(self, ship):
        self.shots = Board._mark_surrounding_cells(self.shots, model_to_dict(ship))
        self.save(update_fields=['shots'])

    @staticmethod
    def _mark_surrounding_cells(array, data):
        array = array.copy()
        array[Ship._get_indicies(data, offset=True)] = True
        return array


class Game(models.Model):
    rows = models.IntegerField(validators=[MinValueValidator(
        Board.MIN_SIZE), MaxValueValidator(Board.MAX_SIZE)])
    cols = models.IntegerField(validators=[MinValueValidator(
        Board.MIN_SIZE), MaxValueValidator(Board.MAX_SIZE)])

    is_over = models.BooleanField(default=False)
    winner = models.ForeignKey('Player', on_delete=models.deletion.CASCADE,
                               related_name="winner", null=True, blank=True)
    current = models.ForeignKey('Player', on_delete=models.deletion.CASCADE, related_name="current")
    playerA = models.ForeignKey('Player', on_delete=models.deletion.CASCADE, related_name="playerA")
    playerB = models.ForeignKey('Player', on_delete=models.deletion.CASCADE,
                                related_name="playerB", null=True, blank=True)

    @staticmethod
    def create(username, rows, cols):
        player = Player.create(username, rows, cols)
        return Game.objects.create(rows=rows, cols=cols, playerA=player, current=player)

    def join(self, username):
        player = Player.create(username, self.rows, self.cols)
        self.playerB = player
        self.save(update_fields=['playerB'])

    def next_player(self):
        self.current = self.playerA if self.current != self.playerA else self.playerB
        self.save(force_update=True)

    def shoot(self, player, x, y):
        if player != self.current:
            return
        opponent = self.playerA if self.current == self.playerB else self.playerB
        hit = opponent.board.shoot(x, y)
        if hit:
            self.is_over = True if opponent.board.ships_alive == 0 else False
            self.winner = self.current
            self.save(update_fields=['is_over', 'winner'])
        else:
            self.next_player()


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
        return np.maximum(self.rows, self.cols)

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
