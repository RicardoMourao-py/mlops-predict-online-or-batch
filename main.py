from fastapi import FastAPI, HTTPException, Depends, Body, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import pandas as pd
from mangum import Mangum
from fastapi.staticfiles import StaticFiles
import pickle
import os
import boto3
from datetime import datetime
import json

app = FastAPI()
app.mount("/img", StaticFiles(directory="img"), name="img")

bearer = HTTPBearer()
ml_models = {}

# Create an S3 client
s3_client = boto3.client("s3")
bucket_name_online = "bucket-mlops-predict-online"
bucket_name_batch= "bucket-mlops-predict-batch"

# Create an SQS client
sqs = boto3.client("sqs")

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
        return True
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
async def root(
    username: str = Query(..., description="Nome de usuário"),
    ok_token=Depends(validate_token)
):
    return "Previsões em Lote e em Tempo Real!"

@app.post("/predict-online")
async def predict_online(
    username: str = Query(..., description="Nome de usuário"),
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
    ok_token=Depends(validate_token),
):
    
    # Registro de data/hora da requisição
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Enviar detalhes da requisição ao S3
    request_log = {
        "username": username,
        "timestamp": timestamp,
        "request_body": person.dict()
    }

    s3_client.put_object(
        Bucket=bucket_name_online,
        Key=f"logs/requests/{timestamp}_request.json",
        Body=json.dumps(request_log)
    )

    ohe = ml_models["ohe"]
    model = ml_models["models"]
    person_t = ohe.transform(pd.DataFrame([person.dict()]))
    pred = model.predict(person_t)[0]

    # Enviar detalhes da predição ao S3
    prediction_log = {
        "username": username,
        "timestamp": timestamp,
        "prediction": str(pred)
    }

    s3_client.put_object(
        Bucket=bucket_name_online,
        Key=f"logs/predictions/{timestamp}_prediction.json",
        Body=json.dumps(prediction_log)
    )

    return {
        "prediction": str(pred),
        "username": username
    }

@app.post("/predict-batch")
async def predict_batch(
    username: str = Query(..., description="Nome de usuário"),
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
    ok_token=Depends(validate_token),
):
    """
    Arquitetura de como funciona a predição em lote.

    ![Arquitetura Batch](img/arquitetura_mlops.png)
    """

    try:
        # Registro de data/hora da requisição
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Enviar detalhes da requisição ao S3
        request_log = {
            "username": username,
            "timestamp": timestamp,
            "request_body": person.dict()
        }

        s3_client.put_object(
            Bucket=bucket_name_batch,
            Key=f"logs/requests/{timestamp}_request.json",
            Body=json.dumps(request_log)
        )

        ohe = ml_models["ohe"]
        model = ml_models["models"]
        person_t = ohe.transform(pd.DataFrame([person.dict()]))
        pred = model.predict(person_t)[0]

        # Enviar detalhes da predição ao S3
        prediction_log = {
            "username": username,
            "timestamp": timestamp,
            "prediction": str(pred)
        }

        # Define the queue URL
        queue_url = os.environ.get("DESTINATION_SQS_URL")

        # Send message to the queue
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(prediction_log))
        
        return {
            "prediction": "Predição em batch - Predict armazenado em bucket.",
            "username": username
        }
    except Exception as e:
        return e

# Adaptador Mangum para AWS Lambda
handler = Mangum(app)
