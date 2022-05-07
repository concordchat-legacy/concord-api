# Copyright 2021 Drogon, Inc.
# See LICENSE for more information.
import base64
import binascii

import itsdangerous

from .database import User
from .errors import Forbidden, Unauthorized


def create_token(user_id: int, user_password: str) -> str:
    signer = itsdangerous.TimestampSigner(user_password)
    user_id = str(user_id)
    user_id = base64.b64encode(user_id.encode())

    return signer.sign(user_id).decode()


def verify_token(token: str):
    if token is None or not isinstance(token, str):
        raise Unauthorized()

    if token.startswith('DrogonBot '):
        token = token.replace('DrogonBot ', '')
    elif token.startswith('DrogonUser '):
        token = token.replace('DrogonUser ', '')

    fragmented = token.split('.')
    user_id = fragmented[0]

    try:
        user_id = base64.b64decode(user_id.encode())
        user_id = int(user_id)
    except (ValueError, binascii.Error):
        raise Unauthorized()

    try:
        user: User = User.objects(User.id == user_id).get()
    except:
        raise Unauthorized()

    signer = itsdangerous.TimestampSigner(user.password)

    try:
        signer.unsign(token)

        return user
    except (itsdangerous.BadSignature):
        raise Forbidden()
