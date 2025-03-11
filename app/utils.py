import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import current_app

def upload_to_s3(file, filename):
    try:
        print(f"Завантаження {filename} до S3...")
        s3 = boto3.client(
            's3',
            aws_access_key_id=current_app.config['S3_KEY'],
            aws_secret_access_key=current_app.config['S3_SECRET'],
            region_name=current_app.config['AWS_REGION']
        )
        s3.upload_fileobj(
            file,
            current_app.config['S3_BUCKET'],
            filename
        )
        file_url = f"{current_app.config['S3_LOCATION']}{filename}"
        print(f"Фото успішно завантажено. URL: {file_url}")
        return file_url
    except Exception as e:
        print(f"Помилка завантаження на S3: {e}")
        return None
