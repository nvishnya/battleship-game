from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game.utils import create_player, delete_player, place_ships, create_game, \
    get_random_available_player, get_game_or_error, add_player_to_game, \
    get_game_data, game_shoot, get_player_data


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
        self.player_id = self.player.id
        self.game_id = None
        self.group_name = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.game_id is not None:
            await self.leave()
        await delete_player(self.player_id)

    async def receive_json(self, content):
        command = content.get('command', None)
        if command == 'start':
            await self.start(content['game_id'],
                             content['rows'],
                             content['cols'],
                             content['ships'],
                             content['friend_opponent'])
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
        # await delete_player(self.player_id)

    async def start(self, game_id, rows, cols, ships, friend_opponent):
        await place_ships(self.player_id, rows, cols, ships)
        self.game_id = game_id
        self.group_name = self.get_group_name(game_id)
        self.rows, self.cols = rows, cols
        if not friend_opponent:
            await self.random_opponent()
        else:
            await self.friend_opponent()

    async def random_opponent(self):
        opponent = await get_random_available_player(self.player_id)
        if opponent is None:
            data = await get_player_data(self.player_id)
            await self.send_json({'type': 'waiting-for-opponent', "you": data})
            return
        game = await create_game(self.rows, self.cols, self.player_id, opponent.id)

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
        if self.game_id is None:
            game = await create_game(self.rows, self.cols, self.player_id)
            self.game_id = game.id
            self.group_name = self.get_group_name(self.game_id)

            data = await get_player_data(self.player_id)
            await self.add_players_to_group(self.group_name, game.playerA)
            await self.send_json({'type': 'waiting-for-opponent', "you": data, 'game_id': game.id})
        else:
            game = await get_game_or_error(self.game_id)
            await add_player_to_game(game, self.player_id)
            await self.add_players_to_group(self.group_name, self.player)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "game.start",
                    "group_name": self.group_name,
                    "game_id": self.game_id,
                }
            )

    async def move(self, x, y):
        await game_shoot(self.game_id, self.player_id, x, y)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game.update",
            })

# Handlers for messages sent over the channel layer

    async def game_update(self, event):
        data = await get_game_data(self.game_id, self.player_id)
        await self.send_json(
            {
                "type": event["type"],
                "game": data
            },
        )

    async def game_start(self, event):
        self.game_id = event["game_id"]
        self.group_name = event["group_name"]

        data = await get_game_data(self.game_id, self.player_id)

        await self.send_json(
            {
                "type": event["type"],
                "game": data
            },
        )

    async def opponent_left(self, event):
        await self.send_json(
            {
                "type": event["type"],
            },
        )
        self.leave()
