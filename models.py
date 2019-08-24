import itertools
import random

from enums import GameState


class Block:
    def __init__(self):
        self._showing = False

    def to_dict(self):
        raise NotImplementedError

    @property
    def showing(self):
        return self._showing

    def flip(self):
        self._showing = True


class NumberBlock(Block):
    def __init__(self, number, color):
        super().__init__()
        self._number = number
        self._color = color

    def __repr__(self):
        return f"{self._color}-{self._number}-{'open' if self.showing else 'closed'}"

    def __eq__(self, other):
        return other.color == self.color

    def to_dict(self):
        return {
            'number': self._number,
            'color': self._color,
            'showing': self._showing
        }

    @property
    def number(self):
        return self._number

    @property
    def color(self):
        return self._color


class JokerBlock(Block):
    def __init__(self, color):
        super().__init__()
        self._color = color

    def __repr__(self):
        return f"{self._color}-Joker-{'open' if self.showing else 'closed'}"

    @property
    def color(self):
        return self._color

    def to_dict(self):
        return {
            'color': self._color,
            'showing': self._showing
        }


class Player:
    def __init__(self, name):
        self._name = name
        self._blocks = []
        self._last_draw = None

    def __repr__(self):
        return f"Player: {self._name}"

    def draw_block(self, blocks, index=None):
        if not index:
            random.shuffle(blocks)
            block = blocks.pop()
        else:
            block = blocks.pop(index)
        self._last_draw = block
        self._blocks.append(block)
        self.sort_blocks()

    def sort_blocks(self):
        self._blocks.sort(key=lambda block: block.number)
        self._blocks.sort(key=lambda block: block.color == 'black', reverse=True)

    def guess_block(self, target_player, target_block_index, guess):
        target_block = target_player.deck[target_block_index]
        if target_block.number == guess:
            target_block.flip()
            print('Guessed!')
            return True
        else:
            self._last_draw.flip()
            print('Guess Failed!')
            return False

    @property
    def deck(self):
        return self._blocks


class Game:
    colors = ('white', 'black')

    def __init__(self, *players, include_jokers=False):
        self._blocks = [NumberBlock(number=item[0], color=item[1])
                        for item in itertools.product([i for i in range(12)], self.colors)]
        if include_jokers:
            self._blocks += [JokerBlock(color) for color in self.colors]

        self._player_count = len(players)
        self._player_1 = None
        self._player_2 = None
        self._player_3 = None
        self._player_4 = None

        for index, player in enumerate(players):
            setattr(self, f'_player_{index + 1}', player)

        self._state = GameState.CREATED

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = GameState(value).name

    @property
    def player_1(self):
        return self._player_1

    @property
    def player_2(self):
        return self._player_2

    @property
    def player_3(self):
        return self._player_3

    @property
    def player_4(self):
        return self._player_4

    @property
    def remaining_blocks(self):
        return self._blocks
