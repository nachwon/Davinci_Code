import enum


class BlockColors(enum.Enum):
    BLACK = 'B'
    WHITE = 'W'


class GameState(enum.Enum):
    CREATED = 'C'
    INITIATED = 'I'
    PLAYING = 'P'
    FINISHED = 'F'
