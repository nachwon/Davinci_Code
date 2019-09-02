import enum


class BlockColors(enum.Enum):
    BLACK = 'B'
    WHITE = 'W'


class Actions(enum.Enum):
    ADD_PLAYER = 'add_player'
    UPDATE_GAME = 'update_game'
    START_GAME = 'start_game'
    PICK_BLOCK = 'pick_block'
    TAKE_TURN = 'take_turn'


class PlayerState(enum.Enum):
    NOT_READY = 'N'
    READY = 'R'
    DRAWING = 'D'
    GUESSING = 'G'


class GameState(enum.Enum):
    CREATED = 'C'
    INITIATED = 'I'
    PLAYING = 'P'
    FINISHED = 'F'
