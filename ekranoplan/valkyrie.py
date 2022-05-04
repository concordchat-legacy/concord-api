# Copyright 2021 Redux, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        'cdn.redux.chat',
        folder + '/' + name,
        ExtraArgs={
            'ContentType': content_type or 'binary/octet-stream',
            'ACL': 'public-read',
        },
    )

    del s3
