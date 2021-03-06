from game.serializers import TestQueryParams, ShipSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from game.models import Board, Ship


@api_view(['GET'])
def get_random_board(request):
    qp = TestQueryParams(data=request.query_params)
    qp.is_valid(raise_exception=True)
    ships = Board.generate_initial_board(qp.data['rows'], qp.data['cols'])
    data = map(lambda x: Ship(**x), ships)
    return Response(ShipSerializer(data, many=True).data)
