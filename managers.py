import asyncio
import itertools
import ujson

from enums import GameState, BlockColors, Actions
from models import Game, Block, Player, Turn


class GameManager:
    def __init__(self):
        self._game = None
        self._players = []

    def _initiate_blocks(self, include_jokers=True):
        colors = [color.value for color in BlockColors]
        blocks = [Block(position=index, number=item[0], color=item[1])
                  for index, item in enumerate(itertools.product([i for i in range(12)], colors))]
        if include_jokers:
            blocks += [Block(position=-1, number='-', color=color) for color in colors]
        return blocks

    def initiate_new_game(self, session_id):
        if not self._players:
            raise ValueError('No players...')
        blocks = self._initiate_blocks()
        self._game = Game(*self._players, blocks=blocks, session_id=session_id)
        self._game.state = GameState.INITIATED
        return self._game

    def add_player(self, name, ws):
        player = Player(name=name, ws=ws)
        self._players.append(player)

    def pick_starting_blocks(self, player):
        player = getattr(self.game, f"player_{player}")
        if len(player.deck) < 4:
            player.draw_block(blocks=self.game.remaining_blocks)

        return self.game.to_dict()

    def check_ready(self):
        for player in self._players:
            if not len(player.deck) == 4:
                return
        self.game.state = GameState.PLAYING

    def take_turn(self, turn):
        from_player = getattr(self.game, f'player_{turn.from_player_id}')  # type: Player
        to_player = getattr(self.game, f'player_{turn.to_player_id}')      # type: Player
        from_player.guess_block(target_player=to_player, target_block_index=turn.target, guess=turn.guess)

        return self.game.to_dict()

    async def update_game(self, message):
        if message.action == Actions.PICK_STARTING:
            message = self.pick_starting_blocks(message.body['player'])
        elif message.action == Actions.TAKE_TURN:
            turn = Turn(**message.body)
            message = self.take_turn(turn)

        print(message)

        await self._distribute_message(message=message)

    async def _distribute_message(self, message):
        tasks = [asyncio.ensure_future(player.ws.send(ujson.dumps(message)))
                 for player in self._players]
        await asyncio.gather(*tasks)

    @property
    def game(self):
        return self._game
