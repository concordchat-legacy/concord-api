import random
import datetime
import orjson
from flask import Blueprint, request
from ..database import create_user
from ..randoms import _id, hashed
from ..errors import Forbidden

bp = Blueprint('_user_management', __name__)

@bp.route('', methods=['POST', 'PUT'], strict_slashes=False)
async def _create_user():
    data: dict = request.get_json(True)
    if data.get('_admin_auth', '') != '972226479407022080':
        raise Forbidden()
    id = _id()

    username = data['username']
    discrim = random.randint(1000, 9999)
    email = data['email']
    password = hashed(data.pop('password'))
    flags = 1 << 0
    avatar_url = ''
    banner_url = ''
    bio = ''
    _default_settings = {'accept_friend_requests': True, 'accept_dms': True}

    user = create_user(
        id=id,
        username=username,
        discriminator=discrim,
        email=email,
        password=password,
        flags=flags,
        avatar=avatar_url,
        banner=banner_url,
        bio=bio,
        settings=_default_settings
    )

    user['id'] = user.pop('_id')

    return orjson.dumps(dict(user))
