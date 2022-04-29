import boto3
import os
import dotenv

dotenv.load_dotenv()

def upload(name: str, folder: str, obj: bytes):
    s3 = boto3.client(
        's3',
        region_name='ap-northeast-1',
        aws_access_key_id=os.getenv('ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('ACCESS_SECRET_KEY')
    )

    s3.upload_fileobj(obj, 'silicondb', folder + '/' + name)

    del s3
