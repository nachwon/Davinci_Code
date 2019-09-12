import pytest

from enums import GameState
from managers import GameManager
from tests.message_builder import TestMessage


class FakeWebSocket:
    async def send(self, *args, **kwargs):
        pass

    async def recv(self, *args, **kwargs):
        pass


@pytest.fixture(scope='function')
async def initiate_game():
    session_id = '1'
    manager = GameManager(session_id=session_id)
    await manager.add_player(name='Tester_1', ws=FakeWebSocket())
    await manager.add_player(name='Tester_2', ws=FakeWebSocket())
    await manager.initiate_new_game()
    yield manager


class TestBlockModel:
    def test_game_instantiation(self):
        session_id = '1'
        manager = GameManager(session_id=session_id)

        assert manager.game._session_id == session_id
        assert manager.game.state == GameState.CREATED
        assert manager.game.players == []

    @pytest.mark.asyncio
    async def test_game_initiation(self):
        session_id = '1'
        manager = GameManager(session_id=session_id)

        with pytest.raises(ValueError) as e:
            await manager.initiate_new_game()
        assert e.value.args[0] == 'No players...'

        await manager.add_player(name='Tester_1', ws=FakeWebSocket())

        with pytest.raises(ValueError) as e:
            await manager.initiate_new_game()
        assert e.value.args[0] == 'Not enough players...'

        await manager.add_player(name='Tester_2', ws=FakeWebSocket())

        await manager.initiate_new_game()

        assert manager.game.state == GameState.INITIATED
        assert len(manager.game.players) == 2
        assert manager.game.player_1 is not None
        assert manager.game.player_2 is not None
        assert manager.game.player_3 is None
        assert manager.game.player_4 is None
        assert len(manager.game.remaining_blocks) == 24

    @pytest.mark.parametrize('number_of_blocks, game_state', [
        (1, GameState.INITIATED),
        (2, GameState.INITIATED),
        (3, GameState.INITIATED),
        (4, GameState.PLAYING)
    ])
    @pytest.mark.asyncio
    async def test_pick_starting_blocks(self, initiate_game, number_of_blocks, game_state):
        manager = initiate_game
        message_builder = TestMessage(action='pick_block')

        block_index = 0
        for player_id in [1, 2]:
            go_on = True
            while go_on:
                message = message_builder.build(player_id=player_id, block_index=block_index)
                await manager.update_game(message)
                block_index += 1
                if block_index > 0 and block_index % number_of_blocks == 0:
                    go_on = False

        assert manager.game.state == game_state
        assert len(manager.game.player_1.deck) == number_of_blocks
        assert len(manager.game.player_2.deck) == number_of_blocks
