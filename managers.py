import asyncio
import itertools
import random

from enums import GameState, BlockColors, Actions
from models import Game, Block, Player, Turn, Response
from serializers import GameSerializer, ResponseSerializer


class GameManager:
    def __init__(self, session_id):
        self._game = Game(session_id=session_id)
        self._waiting = []
        self._players = []
        self._turn = None

    async def initiate_new_game(self):
        if not self._players:
            raise ValueError('No players...')

        if len(self._players) < 2:
            raise ValueError('Not enough players...')

        blocks = self._initiate_blocks()
        self.game.remaining_blocks = blocks
        self.game.state = GameState.INITIATED

        message = {
            "action": "start_game",
            "message": "Pick 4 starting blocks!!",
            "body": None
        }

        response = Response(**message)

        await self._distribute_response(response=response)
        await self._distribute_game()
        return self.game

    def add_waiting(self, ws):
        self._waiting.append(ws)

    async def notify_waiting(self):
        serialized_game = GameSerializer(self.game).serialize()
        tasks = [ws.send(serialized_game) for ws in self._waiting]
        await asyncio.gather(*tasks)

    async def add_player(self, name, ws):
        player = Player(name=name, ws=ws)
        action = "add_player"

        if len(self._players) > 4:
            response = Response(action=action,
                                message='"Game is already full"')

        elif player in self._players:
            response = Response(action=action,
                                message=f"{player.name} already exists")

        else:
            self._players.append(player)
            player_id = self._players.index(player) + 1

            setattr(self.game, f"player_{player_id}", player)

            response = Response(action=action,
                                message=f'Player added! Player ID: {player_id}',
                                body={
                                    "player_id": player_id,
                                    **player.to_dict()
                                })

        await self._send_response(response=response, player=player)
        await self._distribute_game(to_waiting=True)

    def pick_starting_blocks(self, player, index):
        player = getattr(self.game, f"player_{player}")
        if len(player.deck) < 4:
            player.draw_block(blocks=self.game.remaining_blocks, index=index)

        self._check_ready()

        return self.game

    def take_turn(self, turn: Turn):
        from_player = getattr(self.game, f'player_{turn.from_player_id}')  # type: Player
        to_player = getattr(self.game, f'player_{turn.to_player_id}')      # type: Player
        from_player.guess_block(target_player=to_player, target_block_index=turn.target, guess=turn.guess)

        return self.game

    async def update_game(self, message):
        if Actions(message.action) == Actions.PICK_BLOCK:
            self.pick_starting_blocks(message.body['player_id'], message.body['block_index'])

        elif Actions(message.action) == Actions.TAKE_TURN:
            turn = Turn(**message.body)
            self.take_turn(turn)

        await self._distribute_game()

    @staticmethod
    def _initiate_blocks():
        colors = [color.value for color in BlockColors]
        blocks = [Block(position=index, number=item[0], color=item[1])
                  for index, item in enumerate(itertools.product([i for i in range(12)], colors))]
        random.shuffle(blocks)
        return blocks

    def _check_ready(self):
        if self.game.state != GameState.INITIATED:
            return

        for player in self._players:
            if not len(player.deck) == 4:
                return

        self._add_joker_and_shuffle()
        self.game.state = GameState.PLAYING

    def _add_joker_and_shuffle(self):
        colors = [color.value for color in BlockColors]
        jokers = [Block(position=-1, number='-', color=color) for color in colors]
        self.game.remaining_blocks += jokers

        random.shuffle(self.game.remaining_blocks)

    async def _distribute_game(self, to_waiting=False):
        response = Response(action=Actions.UPDATE_GAME.value, body=self.game.to_dict())
        serialized_response = ResponseSerializer(response).serialize()
        if to_waiting:
            tasks = [asyncio.ensure_future(ws.send(serialized_response))
                     for ws in self._waiting]
        else:
            tasks = [asyncio.ensure_future(player.ws.send(serialized_response))
                     for player in self._players]
        await asyncio.gather(*tasks)

    async def _distribute_response(self, response):
        serialized_response = ResponseSerializer(response).serialize()
        tasks = [asyncio.ensure_future(player.ws.send(serialized_response))
                 for player in self._players]
        await asyncio.gather(*tasks)

    @staticmethod
    async def _send_response(response, player):
        serialized_response = ResponseSerializer(response).serialize()
        await player.ws.send(serialized_response)

    @property
    def game(self):
        return self._game
