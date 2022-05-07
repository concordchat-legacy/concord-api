# Copyright 2021 Drogon, Inc.
# See LICENSE for more information.
import os

import boto3
import dotenv

dotenv.load_dotenv()


def upload(name: str, folder: str, obj: bytes, content_type: str):
    s3 = boto3.client(
        's3',
        region_name='ap-northeast-1',
        aws_access_key_id=os.getenv('ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('ACCESS_SECRET_KEY'),
    )

    s3.upload_fileobj(
        obj,
        'cdn.concord.chat',
        folder + '/' + name,
        ExtraArgs={
            'ContentType': content_type or 'binary/octet-stream',
            'ACL': 'public-read',
        },
    )

    del s3
