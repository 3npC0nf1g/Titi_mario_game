import os
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from collections import Counter

def load_data_from_directory(directory):
    data_list = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                for item in data:
                    if isinstance(item, list):
                        data_list.append(item)
                    else:
                        print(f"Format incorrect dans {filename}: {item}")
    
    # Vérifier la longueur des sous-listes
    lengths = [len(item) for item in data_list]
    if len(set(lengths)) > 1:
        print("Les longueurs des sous-listes sont incohérentes.")
        print(f"Longueurs des sous-listes : {set(lengths)}")

        # Trouver la longueur la plus commune
        most_common_length = Counter(lengths).most_common(1)[0][0]
        print(f"Longueur la plus fréquente : {most_common_length}")

        # Ajuster les longueurs des sous-listes
        normalized_data = []
        for item in data_list:
            if len(item) > most_common_length:
                normalized_data.append(item[:most_common_length])  # Tronquer
            elif len(item) < most_common_length:
                normalized_data.append(item + [0] * (most_common_length - len(item)))  # Compléter
            else:
                normalized_data.append(item)
        
        data_list = normalized_data

    return np.array(data_list)

# Charger les données depuis le dossier 'data'
data_directory = 'data'
try:
    data = load_data_from_directory(data_directory)
    print(f'Données chargées avec succès, forme: {data.shape}')
except Exception as e:
    print(f"Erreur: {e}")

# Convertir les données en tableaux NumPy
X_train = data[:, :-2]  # Toutes les colonnes sauf les deux dernières (positions des zombies et Mario)
Y_train = data[:, -2:]  # Les deux dernières colonnes (move_x, move_y)

print(f'X_train shape: {X_train.shape}')
print(f'Y_train shape: {Y_train.shape}')

# Définir le modèle
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1],)),  # Spécifiez la forme d'entrée ici
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(2)  # 2 sorties : move_x, move_y
])

# Compiler le modèle
model.compile(optimizer='adam', loss=tf.keras.losses.MeanSquaredError())
# Entraîner le modèle
history = model.fit(X_train, Y_train, epochs=50, validation_split=0.2)

# Sauvegarder le modèle
model.save('mario_model.h5')

# Visualisation des courbes de perte
plt.plot(history.history['loss'], label='Perte d\'entraînement')
plt.plot(history.history['val_loss'], label='Perte de validation')
plt.title('Courbes de perte')
plt.xlabel('Époques')
plt.ylabel('Perte')
plt.legend()
plt.show()


