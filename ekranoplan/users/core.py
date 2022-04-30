import random
import uuid
from io import BytesIO

import datauri
import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch, post
from cassandra.cqlengine import query

from ..checks import validate_user
from ..database import SettingsType, User, to_dict
from ..errors import BadData, Forbidden, NotFound
from ..randoms import factory, get_hash, verify_hash
from ..tokens import create_token
from ..utils import AuthHeader, jsonify
from ..valkyrie import upload


class CoreUsers(Controller):
    @get('/users/@me')
    async def get_me(self, auth: AuthHeader):
        me = validate_user(auth.value)

        if me.locale == 'EN_US':
            me.locale = 'en_US'
            me.save()

        me = to_dict(me, True)

        return jsonify(me)

    @get('/users/{int:user_id}')
    async def get_user(self, user_id: int, auth: AuthHeader):
        validate_user(auth.value)

        try:
            user: User = User.objects(User.id == user_id).get()
        except query.DoesNotExist:
            raise NotFound()

        ret = to_dict(user)

        if user.bot:
            ret['pronouns'] = 'Attack Helicopter/AttkHeli'

        if user.locale == 'EN_US':
            user.locale = 'en_US'
            user.save()

        return jsonify(ret)

    @post('/users')
    async def register_user(self, request: Request):
        data: dict = await request.json(orjson.loads)

        username = data['username'][:40]
        # TODO: Implement this better
        discrim = random.randint(1, 9999)
        discrim = int('%04d' % discrim)
        email = data['email']
        password = await get_hash(str(data.pop('password')))
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

        pfp_id = ''
        banner_id = ''

        if data.get('avatar'):
            duri = datauri.DataURI(data.pop('avatar'))

            if not str(duri.mimetype.startswith('image/')) or str(
                duri.mimetype
            ) not in ['image/png', 'image/jpeg', 'image/gif']:
                ...
            else:
                pfp_id = str(uuid.uuid1()) + '.' + duri.mimetype.split('/')[1]
                upload(pfp_id, 'users', BytesIO(duri.data), str(duri.mimetype))

        if data.get('banner'):
            duri = datauri.DataURI(data.pop('banner'))

            if not str(duri.mimetype.startswith('image/')) or str(
                duri.mimetype
            ) not in ['image/png', 'image/jpeg', 'image/gif']:
                ...
            else:
                banner_id = str(uuid.uuid1()) + '.' + duri.mimetype.split('/')[1]
                upload(banner_id, 'users', BytesIO(duri.data), str(duri.mimetype))

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
            avatar=pfp_id,
            banner=banner_id,
        )

        resp = to_dict(user, True)
        resp['token'] = create_token(user_id=user.id, user_password=user.password)

        return jsonify(resp, 201)

    @patch('/users/@me')
    async def edit_me(self, auth: AuthHeader, request: Request):
        # TODO: Edit Avatar and Banner
        me = validate_user(auth.value, stop_bots=True)

        data: dict = await request.json(orjson.loads)

        if data.get('username'):
            me.username = str(data['username'])

        if data.get('pronouns'):
            me.pronouns = str(data['pronouns'])

        if data.get('email'):
            me.email = str(data['email'])

        if data.get('password'):
            me.password = await get_hash(str(data['password']))

        if data.get('discriminator'):
            d = int(str(data['discriminator'])[:4])
            if len(str(d)) != 4:
                raise BadData()
            me.discriminator = d

        if data.get('avatar'):
            duri = datauri.DataURI(data.pop('avatar'))

            if not str(duri.mimetype.startswith('image/')) or str(
                duri.mimetype
            ) not in ['image/png', 'image/jpeg', 'image/gif']:
                ...
            else:
                pfp_id = str(uuid.uuid1()) + '.' + duri.mimetype.split('/')[1]
                upload(pfp_id, 'users', BytesIO(duri.data), str(duri.mimetype))
                me.avatar = pfp_id

        if data.get('banner'):
            duri = datauri.DataURI(data.pop('banner'))

            if not str(duri.mimetype.startswith('image/')) or str(
                duri.mimetype
            ) not in ['image/png', 'image/jpeg', 'image/gif']:
                ...
            else:
                banner_id = str(uuid.uuid1()) + '.' + duri.mimetype.split('/')[1]
                upload(banner_id, 'users', BytesIO(duri.data), str(duri.mimetype))
                me.banner = banner_id

        me = me.save()

        ret = to_dict(me, True)

        return jsonify(ret)

    @get('/users/@me/tokens')
    async def make_token(self, request: Request):
        data = await request.json(orjson.loads)
        email, password = data['email'], data['password']

        me = User.objects(User.email == str(email)).allow_filtering().get()

        ok = await verify_hash(me.password, str(password))

        if not ok:
            raise Forbidden()

        token = create_token(me.id, me.password)

        return jsonify([token], 201)
