import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load .env to get credentials
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

bucket = os.getenv('S3_BUCKET')
region = os.getenv('S3_REGION')
endpoint = os.getenv('B2_ENDPOINT')
key_id = os.getenv('B2_KEY_ID')
app_key = os.getenv('B2_APPLICATION_KEY')

s3 = boto3.client(
    's3',
    region_name=region,
    endpoint_url=endpoint,
    aws_access_key_id=key_id,
    aws_secret_access_key=app_key,
)

try:
    print(f"Listing buckets using endpoint: {endpoint}")
    response = s3.list_buckets()
    print("Buckets:", [b['Name'] for b in response['Buckets']])
    print(f"Checking access to bucket: {bucket}")
    s3.head_bucket(Bucket=bucket)
    print("Access to bucket is OK!")
except ClientError as e:
    print("S3/B2 credential or permission error:", e)
