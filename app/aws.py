import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY )

def upload_file_to_s3(file, bucket_name: str, s3_path: str):
    try:
        s3_client.upload_fileobj(file.file, bucket_name, s3_path)
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credentials not available.")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete credentials provided.")
    except ClientError as e:
        # This is a catch-all for errors including bucket not found, permission errors, etc.
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")

def get_file(file_key: str, bucket_name: str):
    return s3_client.get_object(Bucket=bucket_name, Key=file_key)