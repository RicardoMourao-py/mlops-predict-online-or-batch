from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import pandas as pd
from mangum import Mangum
from fastapi.staticfiles import StaticFiles
import pickle
import os

app = FastAPI()
app.mount("/img", StaticFiles(directory="img"), name="img")

bearer = HTTPBearer()
ml_models = {}

def load_encoder():
    with open("models/ohe.pkl", "rb") as f:
        encoder = pickle.load(f)
    return encoder

def load_model():
    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)
    return model

@app.on_event("startup")
async def load_ml_models():
    ml_models["ohe"] = load_encoder()
    ml_models["models"] = load_model()

def get_username_for_token(token):
    expected = os.environ.get("TOKEN_FASTAPI")
    if token == expected:
        return "pedro1"
    return None

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    username = get_username_for_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": username}

class Person(BaseModel):
    age: int
    job: str
    marital: str
    education: str
    balance: int
    housing: str
    duration: int
    campaign: int

@app.get("/")
async def root(user=Depends(validate_token)):
    return "Previsões em Lote e em Tempo Real!"

@app.post("/predict-online")
async def predict_online(
    person: Person = Body(
        default={
            "age": 42,
            "job": "entrepreneur",
            "marital": "married",
            "education": "primary",
            "balance": 558,
            "housing": "yes",
            "duration": 186,
            "campaign": 2,
        },
    ),
    user=Depends(validate_token),
):
    ohe = ml_models["ohe"]
    model = ml_models["models"]
    person_t = ohe.transform(pd.DataFrame([person.dict()]))
    pred = model.predict(person_t)[0]

    return {
        "prediction": str(pred),
        "username": user["username"]
    }

@app.post("/predict-batch")
async def predict_batch(user=Depends(validate_token)):
    """
    Arquitetura de como funciona a predição em lote.

    ![Arquitetura Batch](img/arquitetura_mlops.png)
    """
    return "TO DO: Implementar ainda"
# Adaptador Mangum para AWS Lambda
handler = Mangum(app)
