import boto3
import json

s3_client = boto3.client("s3")
bucket_name = "bucket-mlops-predict-batch"

def lambda_handler(event, context):
    # Read batch of messages
    for record in event["Records"]:
        payload = json.loads(record["body"])

        # Send each message to destination queue
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"logs/predictions/{payload['timestamp']}_prediction.json",
            Body=json.dumps(payload)
        )

    return event["Records"]