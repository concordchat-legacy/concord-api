import random
import orjson
from typing import List
from flask import request
from ..database import User, SettingsType, to_dict
from ..randoms import snowflake, hashed
from ..errors import Forbidden, BadData

async def _create_user():
    data: dict = request.get_json(True)

    if data.get('_admin_auth', '') != '972226479407022080':
        raise Forbidden()
    
    id = snowflake()

    username = data['username']
    # TODO: Implement this better
    discrim = random.randint(1000, 9999)
    email = data['email']
    password = hashed(data.pop('password'))
    flags = 1 << 0
    bio = ''
    locale = data.get('locale') or 'EN_US/EU'

    c: List[dict] = User.objects(username=username, discriminator=discrim).allow_filtering()
    cd: List[dict] = User.objects(username=username).allow_filtering()

    if len(c) != 0:
        raise BadData()

    if len(cd) > 4000:
        raise KeyError()

    user: User = User.create(
        id=snowflake(),
        username=username,
        discriminator=discrim,
        email=email,
        password=password,
        flags=flags,
        bio=bio,
        locale=locale,
        settings=SettingsType(
            accept_friend_requests=True,
            accept_direct_messages=True,
        )
    )

    return orjson.dumps(to_dict(user))