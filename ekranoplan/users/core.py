import random

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, post
from cassandra.cqlengine import query

from ..checks import validate_user
from ..database import SettingsType, User, to_dict
from ..errors import BadData, NotFound
from ..randoms import get_hash, factory
from ..tokens import create_token
from ..utils import AuthHeader, jsonify


class CoreUsers(Controller):
    @get('/users/@me')
    async def get_me(self, auth: AuthHeader):
        me = validate_user(auth.value)

        me = to_dict(me)

        me.pop('password')

        return jsonify(me)

    @get('/users/{int:user_id}')
    async def get_user(self, user_id: int, auth: AuthHeader):
        validate_user(auth.value)

        try:
            user: User = User.objects(User.id == user_id).get()
        except query.DoesNotExist:
            raise NotFound()

        ret = to_dict(user)

        ret.pop('password')
        ret.pop('email')
        ret.pop('settings')

        return jsonify(ret)

    @post('/users')
    async def register_user(self, request: Request):
        data: dict = await request.json(orjson.loads)

        username = data['username']
        # TODO: Implement this better
        discrim = random.randint(1, 9999)
        discrim = int('%04d' % discrim)
        email = data['email']
        password = await get_hash(data.pop('password'))
        flags = 1 << 0
        bio = str(data.get('bio')) or ''
        locale = str(data.get('locale') or 'EN_US')
        referrer = request.query.get('utm_source') or ''

        if not isinstance(referrer, str) and not isinstance(referrer, list):
            referrer = str(referrer)
        elif isinstance(referrer, list):
            referrer = str(referrer[0])

        if locale not in ['EN_US']:
            raise BadData()

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
            referrer=referrer,
        )

        resp = to_dict(user)
        resp['token'] = create_token(user_id=user.id, user_password=user.password)

        return jsonify(resp, 201)
