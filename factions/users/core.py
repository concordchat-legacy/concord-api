import orjson as json
from quart import Response, Blueprint, request
from ..db import users as db
from ..randoms import hashed, snowflake
from ..errors import InvalidData
from ..ratelimiter import limiter

users = Blueprint('users', __name__)

@users.route('', strict_slashes=False, methods=['POST'])
@limiter.limit('3/hour')
async def create_user():
    req = await request.get_json(True)

    if not isinstance(req, dict):
        raise InvalidData('Data is not json')

    user = await db.find_one({'email': req['email']})

    if user != None:
        raise InvalidData('Email is already taken')

    password = hashed(req.pop('password'))

    if len(req['username']) > 30:
        raise InvalidData('Username is too long')

    data = {
        '_id': req['username'],
        'email': req['email'],
        'password': password,
        'avatar_url': '',
        'banner_url': '',
        'bio': '',
        'bot': False,
        'flags': 1 << 1,
        'accept_followers': True,
        'follower_only_posts': False,
        'blocked_users': [],
        'session_ids': [hex(int(snowflake()))],
    }

    d = data.copy()

    await db.insert_one(data)

    return Response(json.dumps(d), 201)
