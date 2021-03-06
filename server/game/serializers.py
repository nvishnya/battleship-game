from rest_framework import serializers, fields
from game.models import Game, Board, Ship, Player
import json
import numpy as np


class TestQueryParams(serializers.Serializer):
    rows = fields.IntegerField(min_value=Board.MIN_SIZE, max_value=Board.MAX_SIZE)
    cols = fields.IntegerField(min_value=Board.MIN_SIZE, max_value=Board.MAX_SIZE)


class ShipSerializer(serializers.ModelSerializer):
    length = serializers.ReadOnlyField()
    orientation = serializers.ReadOnlyField()

    class Meta:
        model = Ship
        fields = ['x', 'y', 'rows', 'cols', 'length', 'orientation']


class NDarrayField(serializers.Field):
    def to_representation(self, value):
        return json.dumps(value.tolist())

    def to_internal_value(self, data):
        data = json.loads(data)
        return np.array(data)


class YouSerializer(serializers.ModelSerializer):
    board = NDarrayField(source='board.board')
    shots = NDarrayField(source='board.shots')

    class Meta:
        model = Player
        fields = ['board', 'shots', ]


class OpponentSerializer(serializers.ModelSerializer):
    shots = serializers.SerializerMethodField()
    shot_ships = serializers.SerializerMethodField()
    
    def _get_shot_ships(self, obj):
        if not hasattr(self, '_shot_ships'):
            self._shot_ships = obj.board.shot_ships
        return self._shot_ships
    
    class Meta:
        model = Player
        fields = ['shots', 'shot_ships']

    def get_shots(self, obj):
        shot_ships = self._get_shot_ships(obj)
        data = obj.board.get_shots_with_marked(shot_ships)
        return NDarrayField().to_representation(data)

    def get_shot_ships(self, obj):
        return ShipSerializer(self._get_shot_ships(obj), many=True).data


class GameSerializer(serializers.ModelSerializer):
    your_turn = serializers.SerializerMethodField()
    you = serializers.SerializerMethodField()
    opponent = serializers.SerializerMethodField()
    you_won = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['your_turn', 'you', 'opponent', 'is_over', 'you_won']

    def get_your_turn(self, obj):
        player = self._context.get("player")
        return True if obj.current == player else False

    def get_you(self, obj):
        player = self._context.get("player")
        return YouSerializer(player).data

    def get_opponent(self, obj):
        player = self._context.get("player")
        opponent = obj.playerB if player == obj.playerA else obj.playerA
        return OpponentSerializer(opponent).data

    def get_you_won(self, obj):
        player = self._context.get("player")
        return True if obj.winner == player else False 
