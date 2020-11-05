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
        fields = ['username', 'board', 'shots', ]


class OpponentSerializer(serializers.ModelSerializer):
    shots = NDarrayField(source='board.shots_with_marked')

    class Meta:
        model = Player
        fields = ['username', 'shots']


class GameSerializer(serializers.ModelSerializer):
    current = serializers.SerializerMethodField()
    you = serializers.SerializerMethodField()
    opponent = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['rows', 'cols', 'current', 'you', 'opponent']

    def get_current(self, obj):
        player = self._context.get("player")
        return 'you' if obj.current == player else 'opponent'

    def get_you(self, obj):
        player = self._context.get("player")
        return YouSerializer(player).data

    def get_opponent(self, obj):
        player = self._context.get("player")
        opponent = obj.playerB if player == obj.playerA else obj.playerA
        return OpponentSerializer(opponent).data