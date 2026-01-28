import asyncio
import websockets

async def test_connection():
    uri = "ws://127.0.0.1:8000/ws_test"
    try:
        async with websockets.connect(uri) as websocket:
            with open("ws_result.txt", "w") as f:
                f.write("Connected\n")
            await websocket.send("Test Message")
            response = await websocket.recv() # Connected message
            response_echo = await websocket.recv() # Echo message
            with open("ws_result.txt", "a") as f:
                f.write(f"Received: {response_echo}\n")
    except Exception as e:
        with open("ws_result.txt", "w") as f:
            f.write(f"Failed: {e}\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except Exception as e:
         with open("ws_result.txt", "w") as f:
            f.write(f"Script Error: {e}\n")
