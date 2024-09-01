import asyncio
import websockets

connected_clients = set()
TIME_OUT_RECONNECT = 0.2
PORT = 8765
HOST = "localhost"

async def broadcast_message(message, sender):
    tasks = []

    for client in connected_clients.copy():
        if client != sender:
            if client.open:
                try:
                    tasks.append(client.send(message))
                except websockets.exceptions.ConnectionClosedOK:
                    print(f"Connexion fermée normalement avec {client}.")
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Erreur de connexion avec {client}: {e}")
                except Exception as e:
                    print(f"Erreur inattendue avec {client}: {e}")
            else:
                # Retirer le client de la liste s'il n'est pas ouvert
                connected_clients.remove(client)
                print(f"Client {client} retiré de la liste des clients connectés.")

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

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

async def start_server():
    global HOST, PORT
    while True:
        try:
            server = await websockets.serve(handle_connection, HOST, PORT)
            print(f"WebSocket server started on ws://{HOST}:{PORT}")

            await server.wait_closed()

        except Exception as e:
            print(f"Erreur du serveur: {e}. Relance du serveur dans {TIME_OUT_RECONNECT} secondes...")
            await asyncio.sleep(TIME_OUT_RECONNECT)

async def main():
    try:
        await start_server()
    except KeyboardInterrupt:
        print("Server stopped manually.")

if __name__ == "__main__":
    asyncio.run(main())
