from features.build_features import TextPreprocessor
from features.build_features import ImagePreprocessor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.sequence import pad_sequences
import logging
import os


# Use the GitHub Actions temporary directory
temp_dir = os.getenv('RUNNER_TEMP', '/tmp')  # Default to /tmp if RUNNER_TEMP is unavailable
log_file = os.path.join(temp_dir, 'inferenceApi_Predict.log')

logging.basicConfig(filename=log_file, level=logging.INFO)

app = FastAPI()

# Charger le tokenizer
with open("../models/tokenizer_config.json", "r", encoding="utf-8") as json_file:
    tokenizer_config = json_file.read()
tokenizer = keras.preprocessing.text.tokenizer_from_json(tokenizer_config)

# Charger le modèle EfficientNet-LSTM
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, '..', 'models', 'JG_model_EfficientNetB0-LSTM.keras')
efficientnet_lstm_model = keras.models.load_model(model_path)
#efficientnet_lstm_model = keras.models.load_model("../models/JG_model_EfficientNetB0-LSTM.keras")
logging.info("Model loaded successfully.")

# Charger le mapper
with open("../models/mapper.json", "r") as json_file:
    mapper = json.load(json_file)

# Initialiser les préprocesseurs
text_preprocessor = TextPreprocessor()
image_preprocessor = ImagePreprocessor()

class InputData(BaseModel):
    descriptions: list[str]
    image_paths: list[str]

@app.post("/predict/")
async def predict(data: InputData):
    if not data.descriptions or not data.image_paths:
        raise HTTPException(status_code=400, detail="Descriptions and image paths must not be empty.")

    if len(data.descriptions) != len(data.image_paths):
        raise HTTPException(status_code=400, detail="The number of descriptions must match the number of image paths.")

    # Prétraitement des textes
    df_text = pd.DataFrame(data.descriptions, columns=["description"])
    text_preprocessor.preprocess_text_in_df(df_text, columns=["description"])

    sequences = tokenizer.texts_to_sequences(df_text["description"])
    padded_sequences = pad_sequences(sequences, maxlen=100, padding="post", truncating="post")

    # Prétraitement des images
    images = []
    for path in data.image_paths:
        try:
            img = load_img(path, target_size=(128, 128, 3))
            img_array = img_to_array(img)
            img_array = preprocess_input(img_array)
            images.append(img_array)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error loading image {path}: {str(e)}")

    images = np.array(images)

    # Faire les prédictions avec EfficientNet-LSTM
    efficientnet_lstm_proba = efficientnet_lstm_model.predict([padded_sequences, images])

    # Préparation des résultats
    predictions = []
    for i in range(len(data.descriptions)):
        label_code = np.argmax(efficientnet_lstm_proba[i])
        score = float(np.max(efficientnet_lstm_proba[i]))
        predictions.append({
            "label": mapper[str(label_code)],
            "score": score
        })

    return predictions


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

