import asyncio
import websockets
import json
import numpy as np
import random
import os
import hashlib
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MSE

TIME_OUT_RECONNECT = 0.1
URI = "ws://localhost:8765"
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
EPOCH = 20000
BATCH_SIZE = 64
i = 0
count_epoch = 0
MODEL_PATH = 'dqn_model.keras'

class DQNAgent:
    def __init__(self, state_size, action_size, alpha=0.001, gamma=0.9, epsilon=1, epsilon_min=0.01, epsilon_decay=0.995):
        """
        Initialise l'agent DQN avec une politique ε-greedy.
        :param state_size: Taille de l'état d'entrée pour le réseau de neurones.
        :param action_size: Nombre d'actions possibles.
        :param alpha: Taux d'apprentissage.
        :param gamma: Facteur de réduction.
        :param epsilon: Taux d'exploration initial.
        :param epsilon_min: Taux d'exploration minimum.
        :param epsilon_decay: Facteur de décroissance de l'exploration.
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model = self.load_model()

    def build_model(self):
        """
        Construit le modèle de réseau de neurones avec Keras.
        """
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss=MSE, optimizer=Adam(learning_rate=self.alpha))
        return model

    def save_model(self):
        """
        Sauvegarde le modèle de réseau de neurones.
        """
        self.model.save(MODEL_PATH)
        print(f"Modèle sauvegardé à {MODEL_PATH}.")

    def load_model(self):
        """
        Charge le modèle de réseau de neurones depuis le fichier.
        """
        if os.path.exists(MODEL_PATH):
            print(f"Chargement du modèle à partir de {MODEL_PATH}.")
            return load_model(MODEL_PATH, custom_objects={'mse': MSE})
        else:
            print("Aucun modèle sauvegardé trouvé, création d'un nouveau modèle.")
            return self.build_model()

    def remember(self, state, action, reward, next_state, done):
        """
        Stocke l'expérience de l'agent dans sa mémoire.
        """
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        """
        Choisit une action en fonction de la politique ε-greedy.
        """
        if np.random.rand() <= self.epsilon:
            # Exploration : choisir une action aléatoire
            print(f"mode exploration (epsilon={self.epsilon:.4f})")
            return random.randrange(self.action_size)
        # Exploitation : choisir l'action avec la valeur Q maximale
        act_values = self.model.predict(state)
        print(f"mode exploitation (epsilon={self.epsilon:.4f})")
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        """
        Entraîne le modèle de réseau de neurones avec un échantillon aléatoire de la mémoire.
        """
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

    def decay_epsilon(self):
        """
        Réduit epsilon après chaque épisode ou action pour encourager l'exploitation.
        """
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


# Exemple d'utilisation
actions = ["Up", "Down", "Left", "Right", "Stay"]
max_zombies = 200
state_size = 5 + 2 * max_zombies
action_size = len(actions)
agent = DQNAgent(state_size, action_size)

def compute_reward(game_state):
    """
    Fonction de calcul de la récompense.
    """
    if game_state["data"]["collision"]:
        return -1000
    elif game_state["data"]["score"] > 0:
        return 10
    else:
        return -1


############

async def handle_messages(websocket):
    global count_epoch, i, EPOCH, BATCH_SIZE,TIME_OUT_RECONNECT
    while True:
        try:
            previous_state = None
            previous_action = None
            async for message in websocket:
                game_state = json.loads(message)
                print(f"Received game state: {game_state}")

                if game_state.get("type") == "game_state":
                    if websocket.open:
                        i += 1

                        # Construction du vecteur d'état
                        mario_state = [
                            game_state["data"]["mario"]["left"],
                            game_state["data"]["mario"]["top"],
                            game_state["data"]["score"],
                            game_state["data"]["collision"],
                            len(game_state["data"]["zombies"])
                        ]

                        # Ajouter les coordonnées des zombies au vecteur d'état
                        zombie_positions = []
                        for zombie in game_state["data"]["zombies"]:
                            zombie_positions.extend([zombie["left"], zombie["top"]])

                        # Normaliser le vecteur à une taille maximale en remplissant avec des zéros
                        if len(zombie_positions) < 2 * max_zombies:
                            zombie_positions.extend([0] * (2 * max_zombies - len(zombie_positions)))
                        else:
                            # Si plus de zombies que le maximum, tronquer la liste
                            zombie_positions = zombie_positions[:2 * max_zombies]

                        # État final
                        state = np.reshape(np.array(mario_state + zombie_positions), [1, state_size])

                        action = agent.choose_action(state)

                        json_message = json.dumps({"type": "ai_move", "data": actions[action]})
                        await websocket.send(json_message)
                        print(f"Message sent: {json_message}")

                        if previous_state is not None and previous_action is not None:
                            reward = compute_reward(game_state)
                            next_state = np.reshape(np.array(mario_state + zombie_positions), [1, state_size])
                            done = game_state["data"]["collision"]
                            agent.remember(previous_state, previous_action, reward, next_state, done)

                        previous_state = state
                        previous_action = action

                        print(f"count epoch : {count_epoch}")
                        print(f"evolution of a epoch (i) : {i}")
                        if i % EPOCH == 0:
                            agent.decay_epsilon()
                            count_epoch += 1
                            i = 0
                            print("save model")
                            agent.save_model()
                            if len(agent.memory) > BATCH_SIZE :
                                print("launch replay model")
                                agent.replay(BATCH_SIZE)
                                print("launch save after replay model")
                                agent.save_model()

                    else:
                        raise Exception("La connexion WebSocket est fermée.")

        except websockets.exceptions.ConnectionClosedOK:
            print("Connexion fermée normalement.")
            break

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Erreur de connexion: {e}")
            print("Tentative de reconnexion...")
            await asyncio.sleep(TIME_OUT_RECONNECT)
            break

        except Exception as e:
            print(f"Erreur inattendue: {e}")
            await asyncio.sleep(TIME_OUT_RECONNECT)
            break
    print(f"AI agent try reconnected on {URI}")

async def connect_to_server(uri):
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connecté au serveur: {uri}")
                await handle_messages(websocket)

        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.InvalidHandshake):
            print(f"Erreur lors de la connexion ou de la transmission au serveur {uri}. Nouvelle tentative dans {TIME_OUT_RECONNECT} secondes...")
            await asyncio.sleep(TIME_OUT_RECONNECT)

        except Exception as e:
            print(f"Erreur inattendue lors de la connexion: {e}. Nouvelle tentative dans {TIME_OUT_RECONNECT} secondes...")
            await asyncio.sleep(TIME_OUT_RECONNECT)

async def main():
    print(f"AI agent started on {URI}")
    await connect_to_server(URI)

if __name__ == "__main__":
    asyncio.run(main())
