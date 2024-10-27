import bcrypt
from fastapi import FastAPI, Depends, HTTPException, Security, UploadFile, File, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
gateway = APIRouter(default_response_class=JSONResponse)

# Hachage d'un mot de passe à ajouter
hashed_password_example = bcrypt.hashpw("mon_mot_de_passe".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Simuler une base de données d'utilisateurs
users_db = {
    "user2": {
        "username": "user2",
        "full_name": "User Two",
        "email": "user2@example.com",
        "hashed_password": hashed_password_example,  # Utilise le vrai hash ici
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

@gateway.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}

