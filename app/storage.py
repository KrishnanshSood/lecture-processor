import os
import boto3
from botocore.exceptions import ClientError


S3_BUCKET = os.environ.get("S3_BUCKET")
S3_REGION = os.environ.get("S3_REGION", "us-east-1")
B2_ENDPOINT = os.environ.get("B2_ENDPOINT")
B2_KEY_ID = os.environ.get("B2_KEY_ID")
B2_APPLICATION_KEY = os.environ.get("B2_APPLICATION_KEY")

s3 = boto3.client(
    "s3",
    region_name=S3_REGION,
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
)


def upload_fileobj(fileobj, key, ContentType=None):
    extra_args = {}
    if ContentType:
        extra_args["ContentType"] = ContentType
    s3.upload_fileobj(fileobj, S3_BUCKET, key, ExtraArgs=extra_args)
    return f"s3://{S3_BUCKET}/{key}"


def upload_file_path(path, key):
    s3.upload_file(path, S3_BUCKET, key)
    return f"s3://{S3_BUCKET}/{key}"


def download_to_path(key, path):
    s3.download_file(S3_BUCKET, key, path)
