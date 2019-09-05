import ujson

from sanic import Sanic
from sanic.websocket import WebSocketProtocol

from enums import Actions, GameState
from managers import GameManager
from models import Request

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

    await ws.send(ujson.dumps({
        "message": message
    }))
    manager.add_waiting(ws=ws)
    await manager.distribute_game(to_waiting=True)

    while True:
        message = await ws.recv()
        message = Request.deserialize(message)
        print(message.to_dict())

        if GameState(manager.game.state) == GameState.CREATED:
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
