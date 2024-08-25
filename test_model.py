import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from collections import Counter

class ModelTester:
    def __init__(self, model_path):
        try:
            # Chargement du modèle
            self.model = tf.keras.models.load_model(model_path, compile=False)
            print("Modèle chargé avec succès.")
            
            # Recompiler le modèle avec les paramètres d'entraînement d'origine
            self.model.compile(optimizer='adam', loss='mse')
            print("Modèle re-compilé avec succès.")
            
        except Exception as e:
            print(f"Erreur lors du chargement du modèle : {e}")
            raise

    def load_data(self, data_path):
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            # Trouver la longueur la plus fréquente
            lengths = [len(item) for item in data]
            length_counter = Counter(lengths)
            most_common_length, _ = length_counter.most_common(1)[0]
            print(f"Longueur la plus fréquente : {most_common_length}")

            # Ajuster les longueurs des sous-listes
            normalized_data = []
            for item in data:
                if len(item) > most_common_length:
                    normalized_data.append(item[:most_common_length])  # Tronquer
                elif len(item) < most_common_length:
                    normalized_data.append(item + [0] * (most_common_length - len(item)))  # Compléter
                else:
                    normalized_data.append(item)

            data_array = np.array(normalized_data)
            print("Données chargées avec succès.")
            return data_array
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")
            raise

    def evaluate_model(self, X_test, Y_test):
        try:
            loss = self.model.evaluate(X_test, Y_test, verbose=1)
            print(f'Perte sur les données de test : {loss}')
            return loss
        except Exception as e:
            print(f"Erreur lors de l'évaluation du modèle : {e}")
            raise

    def predict(self, X_new):
        try:
            predictions = self.model.predict(X_new, verbose=1)
            print('Prédictions :', predictions)
            return predictions
        except Exception as e:
            print(f"Erreur lors de la prédiction : {e}")
            raise

    def plot_predictions(self, X_test, Y_test, predictions):
        plt.figure(figsize=(14, 7))
        plt.subplot(1, 2, 1)
        plt.scatter(range(len(Y_test)), Y_test[:, 0], color='blue', label='Valeurs réelles')
        plt.scatter(range(len(predictions)), predictions[:, 0], color='red', label='Prédictions')
        plt.title('Prédictions vs Valeurs Réelles (move_x)')
        plt.xlabel('Index')
        plt.ylabel('Valeur')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.scatter(range(len(Y_test)), Y_test[:, 1], color='blue', label='Valeurs réelles')
        plt.scatter(range(len(predictions)), predictions[:, 1], color='red', label='Prédictions')
        plt.title('Prédictions vs Valeurs Réelles (move_y)')
        plt.xlabel('Index')
        plt.ylabel('Valeur')
        plt.legend()

        plt.tight_layout()
        plt.show()        

# Utilisation de la classe
try:
    tester = ModelTester('mario_model.h5')
    test_data = tester.load_data('test_data.json')
    X_test = test_data[:, :-2]
    Y_test = test_data[:, -2:]
    
    # Évaluer le modèle
    tester.evaluate_model(X_test, Y_test)
    
    # Faire des prédictions et les afficher
    predictions = tester.predict(X_test)
    tester.plot_predictions(X_test, Y_test, predictions)

except Exception as e:
    print(f"Erreur générale : {e}")
