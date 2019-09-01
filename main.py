import ujson

from sanic import Sanic
from sanic.websocket import WebSocketProtocol

from enums import Actions, GameState
from managers import GameManager
from serializers import RequestSerializer

app = Sanic()

on_going_sessions = {}


@app.websocket('/feed/<session_id:[0-9]+>/')
async def feed(request, ws, *args, **kwargs):
    session_id = kwargs.get('session_id')
    manager = on_going_sessions.get(session_id)
    if not manager:
        manager = GameManager(session_id)
        on_going_sessions[session_id] = manager
        message = "Game created!!"
    else:
        message = f"Joined the session {session_id}"
    game = manager.game

    await ws.send(ujson.dumps({
        "game_state": game.state.value,
        "message": message,
        "body": None
    }))
    manager.add_waiting(ws=ws)
    await manager._distribute_game(to_waiting=True)

    while True:
        message = await ws.recv()
        message = RequestSerializer().deserialize(message)
        print(message)

        if GameState(game.state) == GameState.CREATED:
            print('Waiting for players...')
            if Actions(message.action) == Actions.ADD_PLAYER:
                await manager.add_player(name=message.body['name'], ws=ws)

            elif Actions(message.action) == Actions.START_GAME:
                print('Game started!!')
                await manager.initiate_new_game()

        elif GameState(manager.game.state) == GameState.INITIATED:
            print('pick starting blocks!!')
            await manager.update_game(message=message)

        elif GameState(manager.game.state) == GameState.PLAYING:
            print('running!!')
            await manager.update_game(message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, protocol=WebSocketProtocol)
