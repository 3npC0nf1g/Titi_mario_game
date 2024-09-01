import asyncio
import websockets
import json
import numpy as np
import random
import os

TIME_OUT_RECONNECT = 0.2
URI = "ws://localhost:8765"
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
EPOCH = 60000
i = 0
count_epoch = 0

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, q_table_file='q_table.json'):
        """
        Initialise l'agent de Q-learning avec une politique ε-greedy.
        :param actions: Liste des actions possibles.
        :param alpha: Taux d'apprentissage.
        :param gamma: Facteur de réduction.
        :param epsilon: Taux d'exploration initial.
        :param epsilon_min: Taux d'exploration minimum.
        :param epsilon_decay: Facteur de décroissance de l'exploration.
        :param q_table_file: Nom du fichier pour sauvegarder/charger la table Q.
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table_file = q_table_file
        self.q_table = self.load_q_table()  # Charger la table Q si elle existe, sinon initialiser une nouvelle table Q

    def get_state_key(self, game_state):
        """
        Convertit l'état du jeu en une clé unique pour la table Q.
        Utilise une représentation de chaîne de caractères pour assurer la compatibilité JSON.
        """
        mario_position = (game_state["data"]["mario"]["left"], game_state["data"]["mario"]["top"])
        zombies_positions = tuple((zombie["left"], zombie["top"]) for zombie in game_state["data"]["zombies"])
        score = game_state["data"]["score"]
        collision = game_state["data"]["collision"]

        state_key = json.dumps({"mario_position": mario_position, "zombies_positions": zombies_positions, "score": score, "collision": collision})
        return state_key

    def initialize_state(self, state_key):
        """
        Initialise les valeurs Q pour un état donné s'il n'est pas déjà présent dans la table Q.
        """
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0 for action in self.actions}

    def choose_action(self, game_state):
        """
        Choisit une action en fonction de la politique ε-greedy.
        """
        state_key = self.get_state_key(game_state)
        self.initialize_state(state_key)

        # Politique ε-greedy avec epsilon décroissant
        if random.uniform(0, 1) < self.epsilon:
            # Exploration : choisir une action aléatoire
            action = random.choice(self.actions)
            print(f"mode exploration (epsilon={self.epsilon:.4f})")
        else:
            # Exploitation : choisir l'action avec la valeur Q maximale
            action = max(self.q_table[state_key], key=self.q_table[state_key].get)
            print(f"mode exploitation (epsilon={self.epsilon:.4f})")

        return action

    def update_q_table(self, prev_state, action, reward, next_state):
        """
        Met à jour la table Q en utilisant la formule de Q-learning.
        """
        prev_state_key = self.get_state_key(prev_state)
        next_state_key = self.get_state_key(next_state)
        self.initialize_state(next_state_key)

        # Calculer la valeur Q pour l'état suivant
        future_reward = max(self.q_table[next_state_key].values())
        
        # Mettre à jour la valeur Q pour l'état actuel
        self.q_table[prev_state_key][action] += self.alpha * (reward + self.gamma * future_reward - self.q_table[prev_state_key][action])

    def decay_epsilon(self):
        """
        Réduit epsilon après chaque épisode ou action pour encourager l'exploitation.
        """
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self):
        """
        Sauvegarde la table Q dans un fichier JSON.
        """
        with open(self.q_table_file, 'w') as f:
            json.dump(self.q_table, f)

    def load_q_table(self):
        """
        Charge la table Q à partir d'un fichier JSON.
        """
        if os.path.exists(self.q_table_file):
            with open(self.q_table_file, 'r') as f:
                return json.load(f)
        else:
            return {}


# Exemple d'utilisation
actions = ["Up", "Down", "Left", "Right", "Stay"]
agent = QLearningAgent(actions)

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
    global count_epoch,i 
    while True:
        try:
            previous_state = None
            previous_action = None
            async for message in websocket:
                game_state = json.loads(message)
                print(f"Received game state: {game_state}")

                # Vérifier le type de message reçu
                if game_state.get("type") == "game_state":
                    if websocket.open:
                        i = i + 1 
                        # Prendre une décision avec l'agent de Q-learning
                        decision = agent.choose_action(game_state)

                        # Envoyer l'action via WebSocket
                        json_message = json.dumps({"type": "ai_move", "data": decision})
                        await websocket.send(json_message)
                        print(f"Message sent: {json_message}")
                        # Si c'est la première action, ignorer la mise à jour Q-table
                        if previous_state is not None and previous_action is not None:
                            # Calculer la récompense
                            reward = compute_reward(game_state)

                            # Mettre à jour la table Q
                            agent.update_q_table(previous_state, previous_action, reward, game_state)

                        # Mettre à jour l'état et l'action précédente
                        previous_state = game_state
                        previous_action = decision
                        
                        print(f"count epoch : {count_epoch}")
                        print(f"evolution of a epoch (i) : {i}")
                        # Sauvegarder la table Q après chaque étape
                        if i % EPOCH == 0 :
                            agent.decay_epsilon()
                            count_epoch = count_epoch + 1
                            i = 0 
                        agent.save_q_table()
                    else:
                        print("La connexion WebSocket est fermée.")

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
    print(f"AI agent try reconnected  on {URI}")

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