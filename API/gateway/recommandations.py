
#######################################################################################################################################################

# # V2 pour avoir une liste deroulante des catégories afin de forcer le user à ne prendre que des catégorie qu'on a prédéfini (sinon open bar...)
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from typing import List, Dict, Literal
import pandas as pd
from enum import Enum
from pydantic import BaseModel

app = FastAPI()
gateway = APIRouter(default_response_class=JSONResponse)

# Créer un DataFrame pour les catégories et les codes
categories_data = {
    "category": ["Catégorie A", "Catégorie B", "Catégorie C", "Nouvelle Catégorie"],
    "code": ["C1", "C2", "C3", "C4"]
}
categories_df = pd.DataFrame(categories_data)

# Exemple de données de produits
products = [
    {"id": 1, "name": "Produit 1", "category": "Catégorie A"},
    {"id": 2, "name": "Produit 2", "category": "Catégorie B"},
    {"id": 3, "name": "Produit 3", "category": "Catégorie A"},
    {"id": 4, "name": "Produit 4", "category": "Catégorie C"},
    {"id": 5, "name": "Produit 5", "category": "Catégorie B"},
]
products_df = pd.DataFrame(products)

   
json_result = categories_df.set_index('code')['category'].to_dict()
# Conversion en chaîne formatée
formatted_string = '\n'.join(f"{key}= \"{value}\"" for key, value in json_result.items())
# print()
class Comment(str, Enum):    
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

# Définir un type Literal pour le modèle
print(categories_df['category'])
print(*categories_df['category'])
Comment = Literal[*categories_df['category']]


@gateway.put("/products/{product_id}")
async def update_product_category(product_id: int, category: Comment, comment: str = None):

    for product in products:
        if product["id"] == product_id:
            product["category"] = category
            # Trouver le code associé à la catégorie
            code = categories_df.loc[categories_df['category'] == category, 'code'].values[0]
            product["code"] = code
            return JSONResponse(content=product)
    
    raise HTTPException(status_code=404, detail="Produit non trouvé")

app.include_router(gateway, prefix="/products_reco", tags=["products_reco"])
