import binascii
import itsdangerous
import base64
from typing import Union
from .errors import Unauthorized, Forbidden
from .database import User, _get_date

def create_token(user_id: Union[int, str], user_password: str):
    signer = itsdangerous.TimestampSigner(user_password)
    user_id = str(user_id)
    user_id = base64.b64encode(user_id.encode())

    return signer.sign(user_id).decode

def verify_token(token: str):
    if token.startswith('ConcordBot '):
        token = token.replace('ConcordBot ', '')
    elif token.startswith('ConcordUser '):
        token = token.replace('ConcordUser', '')
    
    fragmented = token.split('.')
    user_id = fragmented[0]

    try:
        user_id = base64.b64decode(user_id.encode())
        user_id = int(user_id)
    except(ValueError, binascii.Error):
        raise Unauthorized()

    try:
        user: User = User.objects(User.id == user_id).get()
    except:
        raise Unauthorized()
    
    signer = itsdangerous.TimestampSigner(user.password)

    try:
        signer.unsign(token)

        user.last_action = _get_date()

        user.save()

        return user
    except(itsdangerous.BadSignature):
        raise Forbidden()
