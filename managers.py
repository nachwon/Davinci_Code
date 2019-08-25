from enums import GameState
from models import Game


class GameManager:
    def __init__(self):
        self._game = None

    def initiate_new_game(self, *players):
        self._game = Game(*players, include_jokers=False)
        self._game.state = GameState.INITIATED
        return self._game
