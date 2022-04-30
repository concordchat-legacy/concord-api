import random

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch, post
from cassandra.cqlengine import query

from ..checks import upload_image, validate_user
from ..database import User, Meta, to_dict
from ..errors import BadData, Forbidden, NotFound
from ..randoms import factory, get_hash, verify_hash
from ..tokens import create_token
from ..utils import VALID_LOCALES, AuthHeader, jsonify


class CoreUsers(Controller):
    @get('/users/@me')
    async def get_me(self, auth: AuthHeader):
        me = validate_user(auth.value)

        if me.locale == 'en_US':
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

        if user.locale == 'en_US':
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

        if locale not in VALID_LOCALES:
            raise BadData()

        if data.get('avatar'):
            pfp_id = upload_image(str(data['avatar']), 'users')

        if data.get('banner'):
            banner_id = upload_image(str(data['banner']), 'users')
            
        user_id = factory().formulate()

        user: User = User.create(
            id=user_id,
            username=username,
            discriminator=discrim,
            email=email[:100],
            password=password,
            flags=flags,
            bio=bio[:4000],
            locale=locale,
            referrer=referrer,
            pronouns=pronouns,
            avatar=pfp_id,
            banner=banner_id,
        )
        Meta.create(user_id=user_id)

        resp = to_dict(user, True)
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
            me.password = await get_hash(str(data['password']))

        if data.get('discriminator'):
            d = int(str(data['discriminator'])[:4])
            if len(str(d)) != 4:
                raise BadData()
            me.discriminator = d

        if data.get('avatar'):
            me.avatar = (
                upload_image(str(data['avatar']), 'users')
                if data['avatar'] != ''
                else ''
            )

        if data.get('banner'):
            me.banner = (
                upload_image(str(data['banner']), 'users')
                if data['banner'] != ''
                else ''
            )

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
