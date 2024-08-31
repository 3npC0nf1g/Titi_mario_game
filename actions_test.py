import asyncio
import websockets

async def send_messages():
    uri = "ws://localhost:8765"
    messages = ["Left", "Left", "Left", "Up"]
    
    async with websockets.connect(uri) as websocket:
        for message in messages:
            await websocket.send(message)
            print(f"Message sent: {message}")
            await asyncio.sleep(0.5)  # Attendre 500 ms (0.5 seconde)

# Exécuter la fonction principale
asyncio.run(send_messages())
