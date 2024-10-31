from features.build_features import TextPreprocessor
from features.build_features import ImagePreprocessor
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import json
from tensorflow import keras
import pandas as pd
import argparse
import pickle



class Predict:
    def __init__(self, tokenizer, efficientnet_lstm, filepath, imagepath):
        self.tokenizer = tokenizer
        self.efficientnet_lstm = efficientnet_lstm
        self.filepath = filepath
        self.imagepath = imagepath

    def preprocess_image(self, image_path, target_size):
        img = load_img(image_path, target_size=target_size)
        img_array = img_to_array(img)
        img_array = preprocess_input(img_array)
        return img_array

    def predict(self):
        X = pd.read_csv(self.filepath)[:10]  # Limiter aux 10 premiers échantillons
        print("X : ", X)

        text_preprocessor = TextPreprocessor()
        image_preprocessor = ImagePreprocessor(self.imagepath)
        text_preprocessor.preprocess_text_in_df(X, columns=["description"])
        image_preprocessor.preprocess_images_in_df(X)

        sequences = self.tokenizer.texts_to_sequences(X["description"])
        padded_sequences = pad_sequences(sequences, maxlen=10, padding="post", truncating="post")

        # Redimensionnement
        target_size_eff = (64, 64, 3)  # Taille d'entrée attendue par le modèle
        images_eff = X["image_path"].apply(lambda x: self.preprocess_image(x, target_size_eff))
        images_eff = tf.convert_to_tensor(images_eff.tolist(), dtype=tf.float32)

        efficientnet_lstm_proba = self.efficientnet_lstm.predict([padded_sequences, images_eff])

        print(f"efficient : {np.argmax(efficientnet_lstm_proba)}")

        # Obtenir les scores de prédiction
        prediction_scores = np.max(efficientnet_lstm_proba, axis=1)
        return {
            i: {
                "label": str(np.argmax(efficientnet_lstm_proba[i])),
                "score": float(prediction_scores[i])  # Convertir en float pour la lisibilité
            }
            for i in range(len(prediction_scores))
        }


def main():
    parser = argparse.ArgumentParser(description="Input data")

    parser.add_argument("--dataset_path", default="data/preprocessed/X_train_update.csv", type=str, help="File path for the input CSV file.")
    parser.add_argument("--images_path", default="data/preprocessed/image_train", type=str, help="Base path for the images.")
    args = parser.parse_args()

    # Charger les configurations et modèles
    with open("models/tokenizer_config.json", "r", encoding="utf-8") as json_file:
        tokenizer_config = json_file.read()
    tokenizer = keras.preprocessing.text.tokenizer_from_json(tokenizer_config)

    efficientnet_lstm = keras.models.load_model("models/best_model_efficientnet_lstm.keras")

    with open("models/mapper.json", "r") as json_file:
        mapper = json.load(json_file)

    predictor = Predict(
        tokenizer=tokenizer,
        efficientnet_lstm=efficientnet_lstm,
        filepath=args.dataset_path,
        imagepath=args.images_path,
    )

    # Création de l'instance Predict et exécution de la prédiction
    predictions = predictor.predict()

    # Sauvegarde des prédictions
    with open("data/preprocessed/predictions.json", "w", encoding="utf-8") as json_file:
        json.dump(predictions, json_file, indent=2)


if __name__ == "__main__":
    main()