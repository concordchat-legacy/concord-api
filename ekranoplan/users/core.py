import random

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, post, patch
from cassandra.cqlengine import query

from ..checks import validate_user
from ..database import SettingsType, User, to_dict
from ..errors import BadData, NotFound
from ..randoms import factory, get_hash
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

        if user.bot:
            ret['pronouns'] = 'Attack Helicopter'

        return jsonify(ret)

    @post('/users')
    async def register_user(self, request: Request):
        data: dict = await request.json(orjson.loads)

        username = data['username'][:40]
        # TODO: Implement this better
        discrim = random.randint(1, 9999)
        discrim = int('%04d' % discrim)
        email = data['email']
        password = await get_hash(data.pop('password'))
        flags = 1 << 0
        bio = str(data.get('bio')) or ''
        locale = str(data.get('locale') or 'en_US')
        referrer = request.query.get('utm_source') or ''
        pronouns = str(data.get('pronouns') or '')

        if not isinstance(referrer, str) and not isinstance(referrer, list):
            referrer = str(referrer)
        elif isinstance(referrer, list):
            referrer = str(referrer[0])

        if locale not in ['en_US']:
            raise BadData()

        user: User = User.create(
            id=factory().formulate(),
            username=username,
            discriminator=discrim,
            email=email[:100],
            password=password,
            flags=flags,
            bio=bio[:4000],
            locale=locale,
            settings=SettingsType(
                accept_friend_requests=True,
                accept_direct_messages=True,
            ),
            referrer=referrer,
            pronouns=pronouns,
        )

        resp = to_dict(user)
        resp['token'] = create_token(user_id=user.id, user_password=user.password)

        return jsonify(resp, 201)

    @patch('/users/@me')
    async def edit_me(self, auth: AuthHeader, request: Request):
        me = validate_user(auth.value, stop_bots=True)

        data: dict = await request.json(orjson.loads)
    
        if data.get('username'):
            me.username = str(data['username'])

        if data.get('pronouns'):
            me.pronouns = str(data['pronouns'])

        if data.get('email'):
            me.email = str(data['email'])

        if data.get('password'):
            me.password = str(data['password'])

        if data.get('discriminator'):
            me.discriminator = int(str(data['discriminator'])[:4])

        me = me.save()

        ret = to_dict(me)

        return jsonify(ret)
