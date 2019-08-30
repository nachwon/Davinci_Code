import ujson

from models import Block, Message, Game


class ModelSerializer:
    _model = None
    _required_fields = ()

    def __init__(self, value):
        self._value = value

    def _check_required(self, value):
        if not set(value.keys()).issubset(set(self._required_fields)):
            raise ValueError("All the required fields must be provided.")

    def deserialize(self):
        value = ujson.loads(self._value)
        self._check_required(value)
        return self._model(**value)

    def serialize(self):
        return ujson.dumps(self._model.to_dict())


class MessageSerializer(ModelSerializer):
    _model = Message
    _required_fields = ('action', 'body')


class BlockSerializer(ModelSerializer):
    _model = Block


class GameSerializer(ModelSerializer):
    _model = Game
