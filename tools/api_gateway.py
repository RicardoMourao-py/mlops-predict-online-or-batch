import boto3
import os
import random
import string

lambda_function_name = "lambda-mlops-predict-online-or-batch"
api_gateway_name = "gateway-mlops-predict-online-or-batch"

id_num = "".join(random.choices(string.digits, k=7))

api_gateway = boto3.client(
    "apigatewayv2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

lambda_function = boto3.client(
    "lambda",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

# Obter a configuração atualizada da Lambda
lambda_function_get = lambda_function.get_function(FunctionName=lambda_function_name)

# Inicialização da variável para armazenar o ApiId
api_id = None
next_token = None

# Passo 1: Use um loop para lidar com a paginação
while True:
    # Chama get_apis com paginação
    if next_token:
        response = api_gateway.get_apis(NextToken=next_token)
    else:
        response = api_gateway.get_apis()

    # Procura a API pelo nome em cada página de resultados
    for api in response['Items']:
        if api['Name'] == api_gateway_name:
            api_id = api['ApiId']
            break

    # Se encontrou a API, interrompe o loop
    if api_id:
        break

    # Atualiza o next_token para a próxima página, se houver
    next_token = response.get('NextToken')
    if not next_token:
        break

# Verifica se a API foi encontrada
if api_id:
    # Passo 2: Obtenha todas as integrações para essa API
    integrations = api_gateway.get_integrations(ApiId=api_id)
    
    # Itere para obter o IntegrationId
    for integration in integrations['Items']:
        Integration_Id = integration['IntegrationId']
        Integration_URI = integration['IntegrationUri']  # Verifique se a URI é a esperada

    # Atualizar o target da API existente com a nova versão da Lambda
    api_gateway.update_integration(
        ApiId=api_id,
        IntegrationId=Integration_Id,  # Use o IntegrationId da integração existente
        IntegrationUri=Integration_URI,
    )
else:
    # Criar uma nova API caso não exista
    api_gateway_create = api_gateway.create_api(
        Name=api_gateway_name,
        ProtocolType="HTTP",
        Version="1.0",
        RouteKey="ANY /{proxy+}",
        Target=lambda_function_get["Configuration"]["FunctionArn"],
    )
    api_id = api_gateway_create['ApiId']

# Atualizar as permissões para garantir que a API Gateway pode invocar a Lambda
api_gateway_permissions = lambda_function.add_permission(
    FunctionName=lambda_function_name,
    StatementId="api-gateway-permission-statement-" + id_num,
    Action="lambda:InvokeFunction",
    Principal="apigateway.amazonaws.com",
    SourceArn=f"arn:aws:execute-api:{os.getenv('AWS_REGION')}:{os.getenv('AWS_ACCOUNT_ID')}:{api_id}/*",
)

print("API Endpoint:", f"https://{api_id}.execute-api.{os.getenv('AWS_REGION')}.amazonaws.com")