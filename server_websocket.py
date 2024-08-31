import asyncio
import websockets

# Fonction pour gérer la connexion WebSocket
async def handle_connection(websocket, path):
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Traitez le message reçu ici et envoyez une réponse si nécessaire
            response = f"Message received: {message}"
            await websocket.send(response)  # Envoyer une réponse au client
    except Exception as e:
        print(f"Error: {e}")
    finally:
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
