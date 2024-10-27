import boto3
import os

# Provide function name
function_name = "lambda_fastapi_v6"

# Create a Boto3 client for AWS Lambda
lambda_client = boto3.client(
    "lambda",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

# Delete the Lambda function
lambda_client.delete_function(FunctionName=function_name)

print(f"Lambda function {function_name} deleted successfully")