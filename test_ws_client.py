import asyncio
import websockets

async def test_connection():
    uri = "ws://localhost:8000/ws_test"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            await websocket.send("Test Message")
            print("Sent: Test Message")
            response = await websocket.recv()
            print(f"Received: {response}")
            response_echo = await websocket.recv()
            print(f"Received: {response_echo}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
