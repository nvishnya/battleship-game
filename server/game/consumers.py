from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game.utils import can_game_be_joined, create_player, place_ships,\
    create_new_game, add_player_to_game, get_game_data, get_player_data,\
    get_random_opponent, shoot_at, delete_player, leave_game


class GameConsumer(AsyncJsonWebsocketConsumer):
    def update_game_info(self, game_id):
        self.game_id = game_id
        self.game_group = None if game_id is None else "Game_{}".format(game_id)

    async def connect(self):
        self.player = await create_player(self.channel_name)
        self.player_id = self.player.id
        self.update_game_info(None)
        await self.accept()

    async def disconnect(self, close_code):
        if self.game_id is not None:
            await self.leave()
        await delete_player(self.player_id)

    async def add_players_to_game_group(self, *players):
        for player in players:
            await self.channel_layer.group_add(self.game_group, player.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get('action', None)
        if action == 'start':
            await self.start(content['ships'],
                             content['friend_as_opponent'],
                             content['game_to_join_id'])
        elif action == 'shoot':
            await self.shoot(content['x'],
                             content['y'])
        elif action == 'leave':
            await self.leave()

    async def start(self, ships, friend_as_opponent, game_to_join_id):
        if game_to_join_id is not None and not can_game_be_joined(game_to_join_id):
            return
        await place_ships(self.player_id, ships)
        if friend_as_opponent:
            await self.game_with_a_friend_opponent(game_to_join_id)
        else:
            await self.game_with_a_random_opponent()

    async def game_with_a_friend_opponent(self, game_to_join_id):
        if game_to_join_id is None:
            game = await create_new_game(self.player_id)
            self.update_game_info(game.id)
            await self.add_players_to_game_group(self.player)
            await self.channel_layer.group_send(self.game_group, {
                'type': 'game.wait',
                'game_id': self.game_id
            })
        else:
            self.update_game_info(game_to_join_id)
            await add_player_to_game(self.game_id, self.player_id)
            await self.add_players_to_game_group(self.player)
            await self.channel_layer.group_send(self.game_group, {
                'type': 'game.update',
                'action': 'game.start',
                'game_id': self.game_id,
            })

    async def game_with_a_random_opponent(self):
        opponent = await get_random_opponent(self.player_id)
        if opponent is None:
            await self.game_wait({'type': 'game.wait',
                                  'game_id': None})
            return
        game = await create_new_game(self.player_id, opponent.id)
        self.update_game_info(game.id)
        await self.add_players_to_game_group(self.player, opponent)
        await self.channel_layer.group_send(self.game_group, {
            'type': 'game.update',
            'action': 'game.start',
            'game_id': self.game_id
        })

    async def shoot(self, x, y):
        await shoot_at(x, y, self.game_id, self.player_id)
        await self.channel_layer.group_send(self.game_group, {
            'type': 'game.update',
            'action': 'game.update',
            'game_id': self.game_id
        })

    async def leave(self):
        await self.channel_layer.group_discard(
            self.game_group,
            self.channel_name,
        )
        await self.channel_layer.group_send(self.game_group, {
            'type': 'game.leave'
        })
        await leave_game(self.player_id, self.game_id)
        self.update_game_info(None)

    async def game_update(self, event):
        if event['action'] == 'game.start':
            self.update_game_info(event['game_id'])

        data = await get_game_data(event['game_id'], self.player_id)
        await self.send_json({'action': event['action'],
                              'game': data})


    async def game_wait(self, event):
        data = await get_player_data(self.player_id)
        await self.send_json({'action': event['type'],
                              'game_id': self.game_id,
                              'you': data})

    async def game_leave(self, event):
        await self.send_json({'action': event['type']})
        self.leave()
