import tensorflow as tf

# Chargez le modèle
try:
    model = tf.keras.models.load_model('mario_model.h5')
    print("Le modèle a été chargé avec succès.")
    model.summary()
except Exception as e:
    print(f"Erreur lors du chargement du modèle : {e}")



