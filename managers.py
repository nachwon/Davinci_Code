import itertools

from enums import GameState, BlockColors
from models import Game, NumberBlock, JokerBlock


class GameManager:
    def __init__(self):
        self._game = None

    def _initiate_blocks(self, include_jokers=True):
        colors = [color.value for color in BlockColors]
        blocks = [NumberBlock(block_id=index, number=item[0], color=item[1])
                  for index, item in enumerate(itertools.product([i for i in range(12)], colors))]
        if include_jokers:
            blocks += [JokerBlock(color) for color in colors]
        return blocks

    def initiate_new_game(self, *players):
        if not players:
            raise ValueError('No players...')
        blocks = self._initiate_blocks()
        self._game = Game(*players, blocks=blocks)
        self._game.state = GameState.INITIATED
        return self._game
