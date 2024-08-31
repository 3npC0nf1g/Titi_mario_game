import asyncio
import websockets
import json 
import tensorflow as tf
import numpy as np


model = tf.keras.models.load_model('') # Charger le modèle

async def handle_connection(websocket, path):
    async for message in websocket:
        # Recevoir l'état du jeu
        state = np.array(json.loads(message)) # Convertir le JSON en numpy array

        #Prédire l'action à partir de l'état 
        q_values = model.predict(np.expand_dims(state, axis=0))
        action = np.argmax(q_values[0])


        #Envoyer l'action choisie au client 
        await websocket.send(str(action))

start_server = websockets.serve(handle_connection, "location", 8765)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
