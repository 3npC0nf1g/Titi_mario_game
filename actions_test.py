import asyncio
import websockets

async def send_messages():
    uri = "ws://localhost:8765"
    messages = ["Left","Left","Left","Left","Up","Up","Up","Up","Up","Right","Right","Right","Right","Down","Down","Down","Down"]
    
    async with websockets.connect(uri) as websocket:
        for message in messages:
            await websocket.send(message)
            print(f"Message sent: {message}")
            await asyncio.sleep(0.3)  # Attendre 500 ms (0.5 seconde)

while True:
    asyncio.run(send_messages())
