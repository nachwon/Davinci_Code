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

    def __eq__(self, other):
        return self.number == other.number and self.color == other.color

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


class JokerBlock(Block):
    def __init__(self, position, number, color, showing=False):
        super().__init__(position, number, color, showing)
        self._next = None
        self._prev = None

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

    @property
    def prev(self):
        return self._prev

    @prev.setter
    def prev(self, value):
        self._prev = value


class Player(BaseModel):
    def __init__(self, name, ws):
        self._name = name
        self._turn_id = None
        self._ws = ws
        self._deck = []
        self._jokers = []
        self._last_draw = None
        self._state = PlayerState.NOT_READY

    def __repr__(self):
        return f"Player: {self._name}"

    def __eq__(self, other):
        return other.name == self.name

    async def draw_block(self, blocks, index):
        block = blocks.pop(index)
        reorder_joker = False

        # When the player drew a joker
        if block.number == '-':
            response = Response(action=Actions.PLACE_JOKER.value,
                                message="Select position to place a joker!").serialize()
            await self.ws.send(response)
            place_request = await self.ws.recv()
            request = Request.deserialize(place_request)
            position = int(request.body['position'])
            # Placing it at the end
            if position == -1:
                self._deck.append(block)
                block.next = None
                prev_block = self._deck[-2]
                block.prev = prev_block
                if isinstance(prev_block, JokerBlock):
                    prev_block.next = block
            # Placing it in the beginning
            elif position == 0:
                self._deck.insert(position, block)
                next_block = self._deck[1]
                block.next = next_block
                block.prev = None
                if isinstance(next_block, JokerBlock):
                    next_block.prev = block
            # Placing it somewhere in between the blocks
            else:
                self._deck.insert(position, block)
                prev_block = self._deck[position - 1]
                next_block = self._deck[position + 1]
                # If it is placed next to the other joker block, update the other joker block's next or prev as well.
                if isinstance(prev_block, JokerBlock):
                    prev_block.next = block
                elif isinstance(next_block, JokerBlock):
                    next_block.prev = block
                block.next = next_block
                block.prev = prev_block

        # When the player drew a normal block
        else:
            jokers = [(index, block) for index, block in enumerate(self._deck) if isinstance(block, JokerBlock)]
            for item in jokers:
                index, joker = item

                if joker.next is None:
                    single_joker_condition = joker.prev.position < block.position
                elif joker.prev is None:
                    single_joker_condition = block.position < joker.next.position
                else:
                    single_joker_condition = joker.prev.position < block.position < joker.next.position

                # If there are two jokers next to each other,
                # and trying to put down a block that can be placed anywhere next to a joker.
                # For example, my deck is 3, joker, joker, 5 and if I drew a 4 block,
                # it can be 3, 4, joker, joker, 5 or 3, joker, 4, joker, 5 or 3, joker, joker, 4, 5.
                if isinstance(joker.next, JokerBlock):
                    if joker.next.next is None:
                        double_joker_condition = joker.prev.position < block.position
                    elif joker.prev is None:
                        double_joker_condition = block.position < joker.next.next.position
                    else:
                        double_joker_condition = joker.prev.position < block.position < joker.next.next.position

                    # Check if the block is within range.
                    if double_joker_condition:
                        second_joker = joker.next
                        # Send a response and wait for request.
                        response = Response(action="reorder_joker",
                                            message="Select where to place your block.",
                                            body={
                                                "joker": joker.to_dict(),
                                                "double_joker": True
                                            }).serialize()
                        await self.ws.send(response)
                        place_request = await self.ws.recv()
                        request = Request.deserialize(place_request)
                        place = request.body['position']

                        # position can be L, R or C in this case.
                        # Place on the left side of the first joker
                        if place == "L":
                            self._deck.insert(index, block)
                            joker.prev = block
                        # Place between the jokers
                        elif place == "C":
                            self._deck.insert(index + 1, block)
                            joker.next = block
                            second_joker.prev = block
                        # Place on the right side of the second joker
                        elif place == "R":
                            self._deck.insert(index + 2, block)
                            second_joker.next = block
                        else:
                            raise TypeError("Invalid placement!")
                        reorder_joker = True
                        break

                # If the block should be next to a joker,
                # let player choose either left or right side of the joker.
                elif single_joker_condition:
                    response = Response(action="reorder_joker",
                                        message="Select where to place your block.",
                                        body={
                                            "joker": joker.to_dict(),
                                            "double_joker": False
                                        }).serialize()
                    await self.ws.send(response)
                    place_request = await self.ws.recv()
                    request = Request.deserialize(place_request)
                    place = request.body['position']
                    # Place on the left side of the joker
                    if place == "L":
                        self._deck.insert(index, block)
                        joker.prev = block
                    # Place on the right side of the joker
                    elif place == "R":
                        self._deck.insert(index + 1, block)
                        joker.next = block
                    else:
                        raise TypeError("Invalid placement!")
                    reorder_joker = True

            # Normal draw
            if not reorder_joker:
                self._deck.append(block)
        self._last_draw = block
        self.sort_deck()

    def sort_deck(self):
        # Filter out the jokers to a separate list
        no_jokers = list(filter(lambda b: not isinstance(b, JokerBlock), self._deck))
        jokers = list(filter(lambda b: isinstance(b, JokerBlock), self._deck))

        # Sort without jokers using position value
        no_jokers.sort(key=lambda block: block.position)
        # And then, add in the jokers using the index of next block
        for joker in jokers:
            # If no next, just append
            if not joker.next:
                no_jokers.append(joker)
            # Else, insert it into where next block is at
            else:
                try:
                    insert_index = no_jokers.index(joker.next)
                except ValueError:
                    if joker.prev:
                        insert_index = no_jokers.index(joker.prev)
                        insert_index += 1
                    else:
                        insert_index = 0
                no_jokers.insert(insert_index, joker)
        # Replace deck with newly sorted deck
        self._deck = no_jokers

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
            "deck": [block.to_dict() for block in self.deck],
            "state": self.state.value
        }

    def get_ready(self):
        self._state = PlayerState.READY

    def drawing_block(self):
        self._state = PlayerState.DRAWING

    def guessing_block(self):
        self._state = PlayerState.GUESSING

    def guessing_more(self):
        self._state = PlayerState.MORE_GUESS

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
