import random

from enums import GameState, BlockColors


class Block:
    def __init__(self, position, number, color, showing=False):
        self._position = position                   # type: int
        self._number = number                       # type: int or str
        self._color = BlockColors(color).value      # type: str
        self._showing = showing

    def __repr__(self):
        return f"{self._color}-{self._number}-{'open' if self.showing else 'closed'}"

    def to_dict(self):
        return {
            "position": self._position,
            "number": self._number,
            "color": self._color,
            "showing": self._showing
        }

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value - 0.5

    @property
    def number(self):
        return self._number

    @property
    def color(self):
        return self._color

    @property
    def showing(self):
        return self._showing

    def flip(self):
        self._showing = True


class Player:
    def __init__(self, name):
        self._name = name
        self._deck = []
        self._last_draw = None

    def __repr__(self):
        return f"Player: {self._name}"

    def draw_block(self, blocks, index=None):
        if not index:
            random.shuffle(blocks)
            block = blocks.pop()
        else:
            block = blocks.pop(index)

        if block.number == '-':
            joker_position = input(f"Enter position to place Joker block \n {', '.join([str(block.position) for block in self._deck])}")
            block.position = int(joker_position)
        self._last_draw = block
        self._deck.append(block)
        self.sort_deck()

    def sort_deck(self):
        self._deck.sort(key=lambda block: block.position)

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
    def name(self):
        return self._name

    @property
    def deck(self):
        return self._deck


class Game:
    def __init__(self, *players, session_id, blocks):
        self._session_id = session_id
        self._blocks = blocks
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
