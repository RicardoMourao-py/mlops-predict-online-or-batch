import boto3
import os 
from dotenv import load_dotenv

load_dotenv()

# Cria uma sessão com o boto3
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

# Nome do bucket que deseja listar
bucket_name = 'bucket-mlops-predict-online'

# Lista os objetos no bucket
response = s3_client.list_objects_v2(Bucket=bucket_name)

# Verifica se há objetos e exibe seus nomes
if 'Contents' in response:
    for obj in response['Contents']:
        print(obj['Key'])
else:
    print("O bucket está vazio ou não foi encontrado.")
