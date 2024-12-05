import asyncio
import websockets
from datetime import datetime


async def message_handler(websocket):
    print("Client connected")

    try:
        async for message in websocket:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await websocket.send(f"Time From Server: {current_time}")
    except websockets.exceptions.ConnectionClosed as e:
        print("Client disconnected:", e)
    finally:
        # Unregister the client
        print("Client disconnected")

# Start the WebSocket server
async def main():
    server = await websockets.serve(message_handler, "0.0.0.0", 8080)
    print("WebSocket server started on ws://0.0.0.0:8080")
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("Server stopped")

# Run the server
if __name__ == "__main__":
    asyncio.run(main())