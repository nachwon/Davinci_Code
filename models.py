import abc
import ujson

from enums import GameState, BlockColors, PlayerState, Actions


class BaseModel:
    def to_dict(self):
        raise NotImplementedError

    def serialize(self):
        return ujson.dumps(self.to_dict())


class Block(BaseModel):
    def __init__(self, position, number, color, showing=False):
        self._position = position                   # type: int
        self._number = number                       # type: int or str
        self._color = BlockColors(color).value      # type: str
        self._showing = showing

    def __repr__(self):
        return f"{self._color}-{self._number if self._number != '-' else 'Joker'}-{'open' if self.showing else 'closed'}"

    def to_dict(self):
        return {
            "position": self._position,
            "number": self._number,
            "color": self._color,
            "showing": self._showing
        }

    @classmethod
    def deserialize(cls, value):
        value = ujson.loads(value)
        return cls(**value)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

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


class Player(BaseModel):
    def __init__(self, name, ws):
        self._name = name
        self._turn_id = None
        self._ws = ws
        self._deck = []
        self._last_draw = None
        self._state = PlayerState.NOT_READY

    def __repr__(self):
        return f"Player: {self._name}"

    def __eq__(self, other):
        return other.name == self.name

    async def draw_block(self, blocks, index):
        block = blocks.pop(index)

        if block.number == '-':
            response = Response(action=Actions.PLACE_JOKER.value,
                                message="Select position to place a joker!").serialize()
            await self.ws.send(response)
            joker_position = await self.ws.recv()
            block.position = int(joker_position)

        self._last_draw = block
        self._deck.append(block)
        self.sort_deck()

    def sort_deck(self):
        self._deck.sort(key=lambda block: block.position)

    def guess_block(self, target_player, target_block_index, guess):
        target_block = target_player.deck[target_block_index]
        if str(target_block.number) == guess:
            target_block.flip()
            print(guess)
            print('Guessed!')
            return True
        else:
            self._last_draw.flip()
            print(guess)
            print('Guess Failed!')
            return False

    def to_dict(self):
        return {
            "name": self.name,
            "turn_id": self._turn_id,
            "deck": self.deck,
            "state": self.state.value
        }

    def get_ready(self):
        self._state = PlayerState.READY

    def drawing_block(self):
        self._state = PlayerState.DRAWING

    def guessing_block(self):
        self._state = PlayerState.GUESSING

    @property
    def name(self):
        return self._name

    @property
    def turn_id(self):
        return self._turn_id

    @turn_id.setter
    def turn_id(self, value):
        self._turn_id = value + 1

    @property
    def deck(self):
        return self._deck

    @property
    def state(self):
        return self._state

    @property
    def ws(self):
        return self._ws


class Game(BaseModel):
    def __init__(self,  session_id):
        self._session_id = session_id
        self._blocks = []
        self._player_1 = None
        self._player_2 = None
        self._player_3 = None
        self._player_4 = None
        self._players = []
        self._state = GameState.CREATED

        self._turn = None

    def to_dict(self):
        data = {
            "remaining_blocks": self.remaining_blocks,
            "players": [player.to_dict() for player in self.players],
            "game_state": self.state.value,
            "turn": self.turn
        }

        for attr in dir(self):
            if attr.startswith('player_'):
                player = getattr(self, attr)
                if player:
                    data[attr] = player.to_dict()

        return data

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = GameState(value)

    @property
    def player_1(self):
        return self._player_1

    @player_1.setter
    def player_1(self, value):
        assert isinstance(value, Player)
        self._player_1 = value
        self._players.append(value)

    @property
    def player_2(self):
        return self._player_2

    @player_2.setter
    def player_2(self, value):
        assert isinstance(value, Player)
        self._player_2 = value
        self._players.append(value)

    @property
    def player_3(self):
        return self._player_3

    @player_3.setter
    def player_3(self, value):
        assert isinstance(value, Player)
        self._player_3 = value
        self._players.append(value)

    @property
    def player_4(self):
        return self._player_4

    @player_4.setter
    def player_4(self, value):
        assert isinstance(value, Player)
        self._player_4 = value
        self._players.append(value)

    @property
    def remaining_blocks(self):
        return self._blocks

    @remaining_blocks.setter
    def remaining_blocks(self, value):
        self._blocks = value

    @property
    def players(self):
        return self._players

    @property
    def turn(self):
        return self._turn

    def set_turn(self):
        self._turn = 1

    def swap_turn(self):
        self._turn += 1
        if self._turn > len(self._players):
            self._turn = 1


class Guess(BaseModel):
    def __init__(self, to_player_id, target, guess):
        self._to_player_id = to_player_id
        self._target = target
        self._guess = guess

    def to_dict(self):
        return {
            "to_player_id": self.to_player_id,
            "target": self.target,
            "guess": self.guess
        }

    @classmethod
    def deserialize(cls, value):
        value = ujson.loads(value)
        return cls(**value)

    @property
    def to_player_id(self):
        return self._to_player_id

    @property
    def target(self):
        return self._target

    @property
    def guess(self):
        return self._guess


class Request(BaseModel):
    def __init__(self, action, body):
        self._action = action
        self._body = body

    def __repr__(self):
        return f"Message - {self.action}"

    def to_dict(self):
        return {
            "action": self.action,
            "body": self.body
        }

    @classmethod
    def deserialize(cls, value):
        value = ujson.loads(value)
        return cls(**value)

    @property
    def action(self):
        return self._action

    @property
    def body(self):
        return self._body


class Response(BaseModel):
    def __init__(self, action, message=None, body=None):
        self._action = action
        self._message = message
        self._body = body

    def __repr__(self):
        return f"Response - {self.action}"

    def to_dict(self):
        return {
            "action": self.action,
            "message": self.message,
            "body": self.body
        }

    @classmethod
    def deserialize(cls, value):
        value = ujson.loads(value)
        return cls(**value)

    @property
    def action(self):
        return self._action

    @property
    def message(self):
        return self._message

    @property
    def body(self):
        return self._body
