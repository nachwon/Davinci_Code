import ujson

from enums import Actions
from models import Block, Request, Game, Response


class ModelSerializer:
    _model = None
    _required_fields = ()

    def __init__(self, value=None):
        if value and not isinstance(value, self._model):
            raise ValueError("Invalid type received.")
        self._value = value

    def _check_required(self, value):
        if not set(value.keys()).issubset(set(self._required_fields)):
            raise ValueError("All the required fields must be provided.")

    def _validate(self, value):
        pass

    def deserialize(self, value):
        value = ujson.loads(value)
        self._check_required(value)
        self._validate(value)
        return self._model(**value)

    def serialize(self):
        return ujson.dumps(self._value.to_dict())


class BlockSerializer(ModelSerializer):
    _model = Block


class GameSerializer(ModelSerializer):
    _model = Game


class RequestSerializer(ModelSerializer):
    _model = Request
    _required_fields = ('action', 'body')

    def _validate(self, value):
        assert value['action'] in [action.value for action in Actions]


class ResponseSerializer(ModelSerializer):
    _model = Response
