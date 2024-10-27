from fastapi import FastAPI, Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
import pandas as pd

app = FastAPI()
gateway = APIRouter(default_response_class=JSONResponse)

# Exemple de données de produits avec catégorie
products_data = [
    {"id": 1, "name": "Produit 1", "category": "Catégorie A"},
    {"id": 2, "name": "Produit 2", "category": "Catégorie B"},
    {"id": 3, "name": "Produit 3", "category": "Catégorie A"},
    {"id": 4, "name": "Produit 4", "category": "Catégorie C"},
    {"id": 5, "name": "Produit 5", "category": "Catégorie B"},
    {"id": 6, "name": "Produit 6", "category": "Catégorie A"},
    {"id": 7, "name": "Produit 7", "category": "Catégorie C"},
    {"id": 8, "name": "Produit 8", "category": "Catégorie B"},
    {"id": 9, "name": "Produit 9", "category": "Catégorie A"},
    {"id": 10, "name": "Produit 10", "category": "Catégorie C"},
]

# Création d'un DataFrame
products_df = pd.DataFrame(products_data)

@gateway.get("/consult_products", response_model=List[Dict[str, str]])
async def get_products(skip: int = 0, limit: int = Query(10, le=100), category: str = None):
    # Filtrer les produits avec une compréhension de liste
    filtered_products = [
        product for product in products_data
        if category is None or product['category'] == category
    ]

    # Vérifier si le skip est valide
    if skip >= len(filtered_products):
        raise HTTPException(status_code=404, detail="No products found with the given skip value.")

    # Limiter la liste de produits retournée
    result_products = filtered_products[skip: skip + limit]

    # Retourner la réponse JSON
    return JSONResponse(content=result_products)

# Inclure le routeur dans l'application
app.include_router(gateway)

# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='0.0.0.0', port=8000)
