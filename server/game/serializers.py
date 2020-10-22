from rest_framework import serializers, fields
from game.models import Game, Board, Ship, Player


class TestQueryParams(serializers.Serializer):
    rows = fields.IntegerField(min_value=Board.MIN_SIZE, max_value=Board.MAX_SIZE)
    cols = fields.IntegerField(min_value=Board.MIN_SIZE, max_value=Board.MAX_SIZE)


class ShipSerializer(serializers.ModelSerializer):
    length = serializers.ReadOnlyField()
    orientation = serializers.ReadOnlyField()

    class Meta:
        model = Ship
        fields = ['x', 'y', 'rows', 'cols', 'length', 'orientation']


class PlayerSerializer(serializers.ModelSerializer):
    board = serializers.JSONField(source='board.board')
    shots = serializers.JSONField(source='board.shots')
    ships = ShipSerializer(many=True, source='board.ship_set')

    class Meta:
        model = Player
        fields = ['username', 'board', 'shots', 'ships']


class GameSerializer(serializers.ModelSerializer):
    playerA = PlayerSerializer()
    playerA = PlayerSerializer()

    class Meta:
        model = Game
        fields = ['rows', 'cols', 'playerA', 'playerB']
