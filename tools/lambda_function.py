import boto3
import os

# Provide function name: "ex_docker_<INSPER_USERNAME>"
lambda_name = "lambda-mlops-predict-online-or-batch"

# Provide Image URI from before
image_latest = f"{os.getenv('AWS_ACCOUNT_ID')}.dkr.ecr.{os.getenv('AWS_REGION')}.amazonaws.com/mlops-batch-online:latest"

lambda_role_arn = os.getenv("AWS_LAMBDA_ROLE_ARN")

environment_variables = {
    "TOKEN_FASTAPI": os.getenv("TOKEN_FASTAPI"), # Update HERE
}

# Create a Boto3 client for AWS Lambda
lambda_client = boto3.client(
    "lambda",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

# Initialize variables for pagination
functions = []
response = lambda_client.list_functions(MaxItems=1000)

# Append the first batch of functions
functions.extend(response["Functions"])

# Continue retrieving additional pages if NextMarker exists
while "NextMarker" in response:
    response = lambda_client.list_functions(MaxItems=1000, Marker=response["NextMarker"])
    functions.extend(response["Functions"])
    
lambda_exists = False
for function in functions:
    function_name = function["FunctionName"]
    if function_name == lambda_name:
        lambda_exists = True
        break

if lambda_exists:
    print("ATUALIZANDO FUNÇÃO !!!")
    response = lambda_client.update_function_code(
        FunctionName=lambda_name,
        ImageUri=image_latest
    )

    # Atualizar a configuração da função (variáveis de ambiente)
    lambda_client.update_function_configuration(
        FunctionName=lambda_name,
        Environment={"Variables": environment_variables}
    )
    print("FUNÇÃO ATUALIZADA !!!")

else:
    print("CRIANDO NOVA FUNÇÃO !!!")
    response = lambda_client.create_function(
        FunctionName=lambda_name,
        PackageType="Image",
        Code={"ImageUri": image_latest},
        Role=lambda_role_arn,
        Timeout=60,  # Optional: function timeout in seconds
        MemorySize=256,  # Optional: function memory size in megabytes
    )
    print("NOVA FUNÇÃO CRIADA !!!")




    

