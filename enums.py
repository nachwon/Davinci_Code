import enum


class BlockColors(enum.Enum):
    BLACK = 'B'
    WHITE = 'W'


class Actions(enum.Enum):
    ADD_PLAYER = 'add_player'
    UPDATE_GAME = 'update_game'
    START_GAME = 'start_game'
    PICK_BLOCK = 'pick_block'
    PLACE_JOKER = 'place_joker'
    TAKE_TURN = 'take_turn'
    MAKE_GUESS = 'make_guess'
    YIELD_TURN = 'yield_turn'
    GUESS_SUCCESS = 'guess_success'
    GUESS_FAIL = 'guess_fail'


class PlayerState(enum.Enum):
    NOT_READY = 'N'
    READY = 'R'
    DRAWING = 'D'
    GUESSING = 'G'
    MORE_GUESS = 'MG'


class GameState(enum.Enum):
    CREATED = 'C'
    INITIATED = 'I'
    PLAYING = 'P'
    FINISHED = 'F'
