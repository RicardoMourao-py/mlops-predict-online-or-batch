import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Lambda function name: read_write_sqs_<INSPER_USERNAME>
function_name = "lambda-read-sqs-write-s3"

# Origin queue: lambda_origin_queue_INSPER_USERNAME
queue_name = "queue-mlops-predict-batch"

# Timeout in seconds. Default is 3.
timeout = 15

# Lambda basic execution role
lambda_role_arn = os.getenv("AWS_LAMBDA_ROLE_ARN")

# Create a Boto3 client for AWS Lambda
lambda_client = boto3.client(
    "lambda",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

# Read the contents of the zip file that you want to deploy
with open("read_sqs_write_s3.zip", "rb") as f:
    zip_to_deploy = f.read()

lambda_response = lambda_client.update_function_code(
    FunctionName=function_name,
    ZipFile=zip_to_deploy
)

# lambda_response = lambda_client.create_function(
#     FunctionName=function_name,
#     Runtime="python3.10",
#     Role=lambda_role_arn,
#     Handler="read_sqs_write_s3.lambda_handler",
#     Code={"ZipFile": zip_to_deploy},
#     Timeout=timeout
# )

function_arn = lambda_response["FunctionArn"]

print(f"Function ARN: {function_arn}")

event_source_arn = (
    f'arn:aws:sqs:{os.getenv("AWS_REGION")}:{os.getenv("AWS_ACCOUNT_ID")}:{queue_name}'
)

# Configure the function's event source mapping with the SQS queue
# response = lambda_client.create_event_source_mapping(
#     EventSourceArn=event_source_arn,
#     FunctionName=function_arn,
#     BatchSize=2,  # Number of messages to retrieve per batch (optional)
# )

print("Lambda function created and configured with SQS event source mapping.")