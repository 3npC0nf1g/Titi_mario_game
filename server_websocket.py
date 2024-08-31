import asyncio
import websockets

connected_clients = set()

async def broadcast_message(message, sender):
    tasks = []

    for client in connected_clients:
        if client != sender:
            tasks.append(client.send(message))
    
    await asyncio.gather(*tasks)


async def handle_connection(websocket, path):
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await broadcast_message(message, websocket)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")


async def main():
    # Démarrer le serveur WebSocket sur localhost:8765
    server = await websockets.serve(handle_connection, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")

    # Garder le serveur actif en attendant indéfiniment
    try:
        await asyncio.Future()  # Attend indéfiniment
    except KeyboardInterrupt:
        print("Server stopped manually.")

# Exécuter la fonction principale
asyncio.run(main())
