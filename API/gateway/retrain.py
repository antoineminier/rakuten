from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import json
import numpy as np
from fastapi.responses import JSONResponse
import requests
import os
from typing import List
import requests


app = FastAPI()
gateway = APIRouter(default_response_class=JSONResponse)
#Sécurity HTTP Basic

security = HTTPBasic()

# Disctionnaire des ID users

users_credentials = {
    "client": "client",
    "datascientist": "datascientist"
    }



@gateway.post("/api/retrain")
async def retrain(credentials: HTTPBasicCredentials = Depends(security)):


    # Construire la requête vers le service
    service_url = "http://localhost:8001/retrain/"
    payload = {
        # "descriptions": descriptions,
        # "image_paths": image_paths
    }

    # Appeler le service
    response = requests.post(service_url, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error calling the external service.")

    # Retourner la réponse du service
    return JSONResponse(content=response.json(), status_code=response.status_code)
    
