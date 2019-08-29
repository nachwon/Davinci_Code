import enum


class BlockColors(enum.Enum):
    BLACK = 'B'
    WHITE = 'W'


class GameState(enum.Enum):
    CREATED = 'C'
    INITIATED = 'I'
    PLAYING = 'P'
    FINISHED = 'F'


class Actions(enum.Enum):
    ADD_PLAYER = 'add_player'
    START_GAME = 'start_game'
