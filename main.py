from sanic import Sanic
from sanic.websocket import WebSocketProtocol

app = Sanic()


@app.websocket('/feed')
async def feed(request, ws):
    data = 'welcome!!'
    while True:
        await ws.send(data)
        received = await ws.recv()
        if received == 'bye':
            data = 'See ya!'
        else:
            data = received


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, protocol=WebSocketProtocol)
