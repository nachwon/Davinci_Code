from sanic import Sanic
from sanic.websocket import WebSocketProtocol

from enums import Actions, GameState
from managers import GameManager
from serializers import MessageSerializer

app = Sanic()

on_going_sessions = {}


@app.websocket('/feed/<session_id:[0-9]+>/')
async def feed(request, ws, *args, **kwargs):
    session_id = kwargs.get('session_id')
    manager = on_going_sessions.get(session_id)
    if not manager:
        manager = GameManager()
        on_going_sessions[session_id] = manager
    game = manager.game

    while True:
        if not game:
            print('Waiting for players...')
            message = await ws.recv()
            m = MessageSerializer(message).deserialize()
            if Actions(m.action) == Actions.ADD_PLAYER:
                manager.add_player(name=m.body, ws=ws)
                await ws.send(f'Player {m.body} have been added!')
                print(manager._players)

            elif Actions(m.action) == Actions.START_GAME:
                print('Game started!!')
                game = manager.initiate_new_game(session_id)
                await manager._distribute_message(message={
                    "player_1": game.player_1.name,
                    "player_2": game.player_2.name,
                    "remaining_blocks": game.remaining_blocks
                })
        else:
            if GameState(game.state) == GameState.INITIATED:
                print('pick starting blocks!!')
                message = await ws.recv()
                message = MessageSerializer(message).deserialize()
                await manager.update_game(message)
                manager.check_ready()

            elif GameState(game.state) == GameState.PLAYING:
                print('running!!')
                message = await ws.recv()
                message = MessageSerializer(message).deserialize()
                await manager.update_game(message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, protocol=WebSocketProtocol)
