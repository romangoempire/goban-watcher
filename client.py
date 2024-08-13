import asyncio
import websockets


async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send("kata-analyze B 10")
        message = await websocket.recv()
        print(f"Received from server: {message}")

        await websocket.send("pull_moves")
        message = await websocket.recv()
        print(f"Received from server: {message}")


if __name__ == "__main__":
    asyncio.run(listen())
