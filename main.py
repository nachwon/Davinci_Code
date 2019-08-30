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
        manager = GameManager(session_id)
        on_going_sessions[session_id] = manager
    game = manager.game

    while True:
        message = await ws.recv()
        message = MessageSerializer(message).deserialize()

        if GameState(game.state) == GameState.CREATED:
            print('Waiting for players...')
            if Actions(message.action) == Actions.ADD_PLAYER:
                await manager.add_player(name=message.body, ws=ws)
                # await ws.send(f'Player {message.body} have been added!')
                # print(manager._players)

            elif Actions(message.action) == Actions.START_GAME:
                print('Game started!!')
                await manager.initiate_new_game(session_id)

        elif GameState(manager.game.state) == GameState.INITIATED:
            print('pick starting blocks!!')
            await manager.update_game(message)
            manager.check_ready()

        elif GameState(manager.game.state) == GameState.PLAYING:
            print('running!!')
            await manager.update_game(message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, protocol=WebSocketProtocol)
