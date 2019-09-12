from models import Request


class TestMessage:
    def __init__(self, action):
        self._action = action

    def build(self, *args, **kwargs):
        action = getattr(self, f'_action_{self._action}')
        if not action:
            raise AttributeError(f"No action called '{self._action}'.")
        message = action(*args, **kwargs)
        return Request(**message)

    @staticmethod
    def _action_pick_block(player_id, block_index):
        return {
            "action": "pick_block",
            "body": {
                "player_id": player_id,
                "block_index": block_index
            }
        }
