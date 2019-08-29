import itertools

from enums import GameState, BlockColors
from models import Game, Block, Player


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

    def add_player(self, name):
        player = Player(name=name)
        self._players.append(player)
