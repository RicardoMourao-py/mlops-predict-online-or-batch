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
from typing import Optional
import numpy as np

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

def load_classifier():
    with open("models/classifier.pkl", "rb") as f:
        encoder = pickle.load(f)
    return encoder

@app.on_event("startup")
async def load_ml_models():
    ml_models["classifier"] = load_classifier()

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


class Paciente(BaseModel):
    """Classe que descreve as informações de um paciente."""
    vc_tem_lesao_atualmente: Optional[int]
    idade_inicio_problema_atual: Optional[int]
    onde_lesao: Optional[int]
    tipo_cancer_paciente: Optional[int]
    algum_filho_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_filho: Optional[int]
    pai_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_pai: Optional[int]
    mae_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_mae: Optional[int]
    avo_paterno_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_avo_paterno: Optional[int]
    avo_paterna_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_avo_paterna: Optional[int]
    avo_materno_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_avo_materno: Optional[int]
    avo_materna_tem_ou_teve_cancer: Optional[int]
    tipo_cancer_avo_materna: Optional[int]

@app.get("/")
async def root(
    username: str = Query(..., description="Nome de usuário"),
    ok_token=Depends(validate_token)
):
    return "Previsões em Lote e em Tempo Real!"

@app.post("/predict-online")
async def predict_online(
    username: str = Query(..., description="Nome de usuário"),
    person: Paciente = Body(
        default={
            "vc_tem_lesao_atualmente": 1,
            "idade_inicio_problema_atual": 1,
            "onde_lesao": 1,
            "tipo_cancer_paciente": 1,
            "algum_filho_tem_ou_teve_cancer": 1,
            "tipo_cancer_filho": 1,
            "pai_tem_ou_teve_cancer": 1,
            "tipo_cancer_pai": 1,
            "mae_tem_ou_teve_cancer": 1,
            "tipo_cancer_mae": 1,
            "avo_paterno_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_paterno": 1,
            "avo_paterna_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_paterna": 1,
            "avo_materno_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_materno": 1,
            "avo_materna_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_materna": 1
        },
    ),
    ok_token=Depends(validate_token),
):
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
            Bucket=bucket_name_online,
            Key=f"logs/requests/{timestamp}_request.json",
            Body=json.dumps(request_log)
        )

        classifier = ml_models["classifier"]
        data = data.dict()
        list_data=[data[key] for key in data.keys()]
        input_array=np.array([list_data])

        prediction = classifier.predict([list_data])
        probabilidades_teste_positivo=classifier.predict_proba(input_array)[0][1]
        probabilidades_teste_negativo=1-probabilidades_teste_positivo

        if prediction[0]== 1:
            prediction = "Resultado positivo para teste genético:Indica ocorrência de algum tipo de mutação"
        else:
            prediction = "Resultado negativo para teste genético:Não indica ocorrência de mutação"

        # Enviar detalhes da predição ao S3
        prediction_log = {
            "username": username,
            "timestamp": timestamp,
            'prediction': prediction,
            'predictionProba_positivo':round(probabilidades_teste_positivo,2),
            'predictionProba_negativo':round(probabilidades_teste_negativo,2) 
        }

        s3_client.put_object(
            Bucket=bucket_name_online,
            Key=f"logs/predictions/{timestamp}_prediction.json",
            Body=json.dumps(prediction_log)
        )

        return {
            "username": username,
            "timestamp": timestamp,
            'prediction': prediction,
            'predictionProba_positivo':round(probabilidades_teste_positivo,2),
            'predictionProba_negativo':round(probabilidades_teste_negativo,2) 
        }

    except Exception as e:
        return e
    
@app.post("/predict-batch")
async def predict_batch(
    username: str = Query(..., description="Nome de usuário"),
    person: Paciente = Body(
        default={
            "vc_tem_lesao_atualmente": 1,
            "idade_inicio_problema_atual": 1,
            "onde_lesao": 1,
            "tipo_cancer_paciente": 1,
            "algum_filho_tem_ou_teve_cancer": 1,
            "tipo_cancer_filho": 1,
            "pai_tem_ou_teve_cancer": 1,
            "tipo_cancer_pai": 1,
            "mae_tem_ou_teve_cancer": 1,
            "tipo_cancer_mae": 1,
            "avo_paterno_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_paterno": 1,
            "avo_paterna_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_paterna": 1,
            "avo_materno_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_materno": 1,
            "avo_materna_tem_ou_teve_cancer": 1,
            "tipo_cancer_avo_materna": 1
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

        classifier = ml_models["classifier"]
        data = data.dict()
        list_data=[data[key] for key in data.keys()]
        input_array=np.array([list_data])

        prediction = classifier.predict([list_data])
        probabilidades_teste_positivo=classifier.predict_proba(input_array)[0][1]
        probabilidades_teste_negativo=1-probabilidades_teste_positivo

        if prediction[0]== 1:
            prediction = "Resultado positivo para teste genético:Indica ocorrência de algum tipo de mutação"
        else:
            prediction = "Resultado negativo para teste genético:Não indica ocorrência de mutação"

        # Enviar detalhes da predição ao S3
        prediction_log = {
            "username": username,
            "timestamp": timestamp,
            'prediction': prediction,
            'predictionProba_positivo':round(probabilidades_teste_positivo,2),
            'predictionProba_negativo':round(probabilidades_teste_negativo,2) 
        }

        # Define the queue URL
        queue_url = os.environ.get("DESTINATION_SQS_URL")

        # Send message to the queue
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(prediction_log))
        
        return {
            "username": username,
            "timestamp": timestamp,
            'prediction': prediction,
            'predictionProba_positivo':round(probabilidades_teste_positivo,2),
            'predictionProba_negativo':round(probabilidades_teste_negativo,2) 
        }
    except Exception as e:
        return e

# Adaptador Mangum para AWS Lambda
handler = Mangum(app)
