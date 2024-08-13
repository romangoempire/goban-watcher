import json
import asyncio
import websockets
from katago.katago_gtp import KataGo


async def handle_client(websocket, path):
    katago = KataGo()

    try:
        async for message in websocket:
            if message == "pull_moves":
                await websocket.send(json.dumps(katago.read_move()))
            if message.startswith("kata-analyze"):
                katago.send(message)
                await websocket.send("ponder")
            else:
                katago.send(message)
                await websocket.send(katago.read())

    except websockets.ConnectionClosed:
        print("Connection closed by client.")


async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
