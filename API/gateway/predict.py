from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, APIRouter, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd
import json
import numpy as np
from fastapi.responses import JSONResponse
import requests
import os
from typing import List
import requests

from bson import ObjectId
from datetime import datetime


app = FastAPI()
gateway = APIRouter(default_response_class=JSONResponse)
#Sécurity HTTP Basic

security = HTTPBasic()

# Dictionnaire des user IDs
users_credentials = {
    "client": "client",
    "datascientist": "datascientist"
    }

# Données
# Charger les utilisateurs
with open('data/categories_list.json', 'r') as file:
    product_categories = json.load(file)

product_categories_df = pd.DataFrame(product_categories["product_categories"])



class ProduitPredictData(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    # name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    # updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    label_code: Optional[int] = None
    score: Optional[float] = None
    categorie_predict: Optional[str] = None
    user_id: Optional[str] = None
    prediction_date: Optional[datetime] = Field(default_factory=datetime.now)
    # categorie_suggestion: Optional[str] = None
    # updated_suggestion_at: Optional[datetime] = Field(default_factory=datetime.now)
    # comment_categorie_suggestion: Optional[str] = None
    # categorie_final: Optional[str] = None
    # comment_categorie_final: Optional[str] = None

class ProduitSuggetionData(ProduitPredictData):
    categorie_suggestion: Optional[str] = None
    updated_suggestion_at: Optional[datetime] = Field(default_factory=datetime.now)
    comment_categorie_suggestion: Optional[str] = None

class ProduitValidationData(ProduitSuggetionData):
    categorie_final: Optional[str] = None
    comment_categorie_final: Optional[str] = None
    updated_suggestion_at: Optional[datetime] = Field(default_factory=datetime.now)




# Création d'un dossier où placer les images uploadées
current_dir = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(current_dir, '..', 'data', 'images_posted')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@gateway.post("/api/predict")
async def predict(
    descriptions: List[str] = Query(...),
    images: List[UploadFile] = File(...)
):
    image_paths = []

    for file in images:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        image_paths.append(file_path)
        print("image_paths :", image_paths)

    # Vérification de l'égale quantité de descriptions et d'images
    if len(descriptions) != len(image_paths):
        raise HTTPException(status_code=400, detail="The number of descriptions must match the number of images.")

    # Construire la requête vers le service
    service_url = "http://localhost:8001/predict/"
    payload = {
        "descriptions": descriptions,
        "image_paths": image_paths
    }

    # Appeler le service
    response = requests.post(service_url, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error calling the external service.")

    predictions = response.json()  

    # Ajout d'informations pour chaque prédiction
    enriched_predictions = []
    for prediction, desc, img_path in zip(predictions, descriptions, image_paths):
        category_row = product_categories_df[product_categories_df['code_type'] == int(prediction['label'])]
        category_name = category_row['categorie_designation'].values[0] if not category_row.empty else "Inconnue"
        
        enriched_prediction = {
            "label_code": prediction['label'],
            "score": prediction['score'],
            "categorie": category_name,
            "description": desc,
            "image": os.path.basename(img_path),
            "user_id": "007",
            "prediction_date": str(datetime.now())
        }
        enriched_predictions.append(enriched_prediction)

    return JSONResponse(content=enriched_predictions, status_code=response.status_code)




"""
    if response.status_code == 200:
        # Extraire la réponse JSON
        json_data = response.json()
        # Convertir en DataFrame
        df = pd.DataFrame([json_data])
        # Convertir la colonne 'label' en entier
        df['label'] = df['label'].astype(int)
        
        # Afficher le DataFrame ou l'utiliser
        print(df)
        # print("response_df :", response_df)
        category_row = product_categories_df[product_categories_df['code_type'] == df['label'].iloc[0]] # 2403 df['label'].astype(int)

        # Extraire le nom de la catégorie si elle existe, sinon "Inconnue"
        category_name = category_row['categorie_designation'].values[0] if not category_row.empty else "Inconnue"
        # Afficher le résultat
        print(f"La catégorie pour le code 2403 est : {category_name}")
        # Retourner la réponse du service
        if not category_row.empty:
            category_name = category_row['categorie_designation'].values[0]  # Extraire la désignation de la catégorie
        else:
            category_name = "Inconnue"  # Valeur par défaut si aucune catégorie n'est trouvée

        # Ajouter la catégorie au JSON de la réponse
        json_data['categorie'] = category_name

        # Afficher la réponse avec la nouvelle clé "categorie"
        print(json_data)
        json_data['user_id'] = "007"
        json_data['prediction_date'] = "0101204"
        produit_avance = ProduitPredictData()
        produit_avance.user_id = "007"
        produit_avance.prediction_date = "0000000"
        produit_avance.label_code = df['label'].iloc[0]
        produit_avance.user_id = "user_id"
        produit_avance.score = 101204
        produit_avance.description = "nnn"
        produit_avance.image_url = "mmm"

        print(produit_avance)

        ProduitValidation = ProduitValidationData(**produit_avance.dict())
        print(f"ProduitValidationData : {ProduitValidation}")

    else:
        print(f"Erreur : {response.status_code}")
        
    # return JSONResponse(content=response.json(), status_code=response.status_code)
    return JSONResponse(json_data, status_code=response.status_code)
"""

# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='0.0.0.0', port=8000)

app.include_router(gateway, prefix="/predict", tags=["predict"])