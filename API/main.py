from fastapi import FastAPI
from gateway import products, login, recommandations, predict, retrain #, ml
# from fastapi.middleware.cors import CORSMiddleware

# Ajout d'une description et d'un titre pour mieux documenter l'API
app = FastAPI(
    title="API e-commerce avec ML",
    description="API permettant de gérer des produits, des catégories et d'utiliser la classification ML",
    version="1.0.0"
)

# Inclure les routes (endpoints) définies dans les autres fichiers
app.include_router(login.gateway)
app.include_router(predict.gateway)
app.include_router(products.gateway)
app.include_router(recommandations.gateway)
app.include_router(retrain.gateway)

@app.get("/")
def read_root():
    # Message d'accueil pour la route principale
    return {"message": "Bienvenue sur l'API e-commerce avec classification ML"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
