import enum


class GameState(enum.Enum):
    CREATED = 'C'
    INITIATED = 'I'
    PLAYING = 'P'
    FINISHED = 'F'
