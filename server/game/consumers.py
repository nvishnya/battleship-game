from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game.utils import create_player, delete_player, place_ships, create_game, \
    get_random_available_player, get_game_or_error, add_player_to_game, \
    get_game_data, game_shoot


class GameConsumer(AsyncJsonWebsocketConsumer):
    def get_group_name(self, game_id):
        if game_id is None:
            return None
        return 'game_{}'.format(game_id)

    async def add_players_to_group(self, group_name, *players):
        for player in players:
            await self.channel_layer.group_add(group_name, player.channel_name)

    async def connect(self):
        self.player = await create_player(self.channel_name)
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', None)
        self.group_name = self.get_group_name(self.game_id)
        await self.accept()

    async def disconnect(self, close_code):
        if self.game_id is not None:
            await self.leave()

    async def receive_json(self, content):
        command = content.get('command', None)
        if command == 'start':
            await self.start(content['rows'], content['cols'], content['ships'])
        elif command == 'move':
            await self.move(content['x'], content['y'])

# Command helper methods called by receive_json

    async def leave(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "opponent.left",
            }
        )
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        await delete_player(self.player)

    async def start(self, rows, cols, ships):
        await place_ships(self.player, rows, cols, ships)
        self.rows, self.cols = rows, cols
        if self.game_id is None:
            await self.random_opponent()
        else:
            await self.friend_opponent()

    async def random_opponent(self):
        opponent = await get_random_available_player(self.player)
        if opponent is None:
            await self.send_json({'event': 'waiting-for-opponent'})
            return
        game = await create_game(self.rows, self.cols, self.player, opponent)

        self.game_id = game.id
        self.group_name = self.get_group_name(self.game_id)

        await self.add_players_to_group(self.group_name, game.playerA, game.playerB)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game.start",
                "group_name": self.group_name,
                "game_id": self.game_id,
            }
        )

    async def friend_opponent(self):
        game = await get_game_or_error(self.game_id)
        await add_player_to_game(game, self.player)
        
#         if status is False:
#             await self.send_json({'event': 'game-already-started'})
#             return

        await self.add_players_to_group(self.group_name, self.player)
        game = await get_game_or_error(self.game_id)

        if game.playerB_id is None:
            await self.send_json({'event': 'waiting-for-friend'})
        else:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "game.start",
                    "group_name": self.group_name,
                    "game_id": self.game_id,
                }
            )

    async def move(self, x, y):
        await game_shoot(self.game_id, self.player, x, y)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game.update",
            })

# Handlers for messages sent over the channel layer

    async def game_update(self, event):
        data = await get_game_data(self.game_id, self.player)
        await self.send_json(
            {
                "event": event["type"],
                "game": data
            },
        )

    async def game_start(self, event):
        self.game_id = event["game_id"]
        self.group_name = event["group_name"]
        
        data = await get_game_data(self.game_id, self.player)

        await self.send_json(
            {
                "event": event["type"],
                "game": data
            },
        )

    async def opponent_left(self, event):
        await self.send_json(
            {
                "event": event["type"],
            },
        )
        self.leave()
