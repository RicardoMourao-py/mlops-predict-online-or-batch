import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Provide bucket name: log-bucket-YOUR_INSPER_USERNAME
bucket_name = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={"LocationConstraint": os.getenv("AWS_REGION")},
)