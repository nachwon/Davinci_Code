import asyncio
import itertools
import random

from enums import GameState, BlockColors, Actions
from models import Game, Block, Player, Response, Guess, Request


class GameManager:
    def __init__(self, session_id):
        self._game = Game(session_id=session_id)
        self._waiting = []
        self._players = []

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

        await self.distribute_response(response=response)
        await self.distribute_game()
        return self.game

    def add_waiting(self, ws):
        self._waiting.append(ws)

    async def notify_waiting(self):
        serialized_game = self.game.serialize()
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
            player.turn_id = self._players.index(player)
            player_id = player.turn_id

            setattr(self.game, f"player_{player_id}", player)

            response = Response(action=action,
                                message=f'Player added! Player ID: {player_id}',
                                body={
                                    "player_id": player_id,
                                    **player.to_dict()
                                })

        await self.send_response(response=response, player=player)
        await self.distribute_game(to_waiting=True)

    async def pick_starting_blocks(self, player, index):
        player = getattr(self.game, f"player_{player}")
        if len(player.deck) < 4:
            await player.draw_block(blocks=self.game.remaining_blocks, index=index)

        self._check_ready()

        return self.game

    async def take_turn(self, message):
        player = getattr(self.game, f"player_{message.body['player_id']}")
        player.drawing_block()
        await self.pick_block(player=player, index=message.body['block_index'])
        guess_message = await player.ws.recv()
        guess = Guess.deserialize(guess_message)

        await self.guess_block(player, guess=guess)

    async def pick_block(self, player, index):
        await player.draw_block(blocks=self.game.remaining_blocks, index=index)
        player.guessing_block()
        await self.distribute_game()

    async def guess_block(self, player, guess: Guess):
        from_player = player                                                # type: Player
        to_player = getattr(self.game, f'player_{guess.to_player_id}')      # type: Player
        success = from_player.guess_block(target_player=to_player, target_block_index=guess.target, guess=guess.guess)
        await self.distribute_game()
        if success:
            guess_message = await player.ws.recv()
            guess = Guess.deserialize(guess_message)
            await self.guess_block(player, guess)
        else:
            from_player.get_ready()
            self.game.swap_turn()
            next_player = getattr(self.game, f'player_{self.game.turn}')
            next_player.drawing_block()
        return self.game

    async def update_game(self, message):
        if self.game.state == GameState.PLAYING:
            if Actions(message.action) == Actions.TAKE_TURN:
                await self.take_turn(message=message)

        elif self.game.state == GameState.INITIATED:
            if Actions(message.action) == Actions.PICK_BLOCK:
                await self.pick_starting_blocks(message.body['player_id'], message.body['block_index'])

        await self.distribute_game()

    @staticmethod
    def _initiate_blocks():
        colors = [color.value for color in BlockColors]
        blocks = [Block(position=index, number=item[0], color=item[1])
                  for index, item in enumerate(itertools.product([i for i in range(12)], colors))]
        random.shuffle(blocks)
        return blocks

    def _check_ready(self):
        if self.game.state != GameState.INITIATED:
            return False

        for player in self._players:
            if not len(player.deck) == 4:
                return False

        self._add_joker_and_shuffle()
        self.game.state = GameState.PLAYING
        self.game.set_turn()
        self.game.player_1.drawing_block()

        return True

    def _add_joker_and_shuffle(self):
        colors = [color.value for color in BlockColors]
        jokers = [Block(position=-1, number='-', color=color) for color in colors]
        self.game.remaining_blocks += jokers

        random.shuffle(self.game.remaining_blocks)

    async def distribute_game(self, to_waiting=False):
        response = Response(action=Actions.UPDATE_GAME.value, body=self.game.to_dict())
        serialized_response = response.serialize()
        if to_waiting:
            tasks = [asyncio.ensure_future(ws.send(serialized_response))
                     for ws in self._waiting]
        else:
            tasks = [asyncio.ensure_future(player.ws.send(serialized_response))
                     for player in self._players]
        await asyncio.gather(*tasks)

    async def distribute_response(self, response):
        serialized_response = response.serialize()
        tasks = [asyncio.ensure_future(player.ws.send(serialized_response))
                 for player in self._players]
        await asyncio.gather(*tasks)

    @staticmethod
    async def send_response(response, player):
        serialized_response = response.serialize()
        await player.ws.send(serialized_response)

    @property
    def game(self):
        return self._game
