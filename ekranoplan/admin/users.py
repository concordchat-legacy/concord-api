import random
from typing import List

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, post, put

from ..checks import validate_admin
from ..database import SettingsType, User, to_dict
from ..errors import BadData
from ..randoms import factory, get_hash
from ..tokens import create_token
from ..utils import AuthHeader, jsonify


class AdminUsers(Controller):
    @post('/admin/users')
    @put('/admin/users')
    async def _create_user(self, request: Request, auth: AuthHeader):
        data: dict = await request.json(orjson.loads)

        validate_admin(auth.value)

        username = data['username']
        # TODO: Implement this better
        discrim = random.randint(1, 9999)
        discrim = int('%04d' % discrim)
        email = data['email']
        password = await get_hash(data.pop('password'))
        flags = data.get('flags') or 1 << 0
        bio = data.get('bio') or ''
        locale = data.get('locale') or 'EN_US/EU'

        c: List[dict] = User.objects(
            username=username, discriminator=discrim
        ).allow_filtering()
        cd: List[dict] = User.objects(username=username).allow_filtering()

        if len(c) != 0:
            raise BadData()

        if len(cd) > 4000:
            raise KeyError()

        user: User = User.create(
            id=factory().formulate(),
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
            ),
        )

        resp = to_dict(user)
        resp['token'] = create_token(user_id=user.id, user_password=user.password)

        return jsonify(resp)
