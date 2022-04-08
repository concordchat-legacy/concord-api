import orjson
from flask import request
from cassandra.cqlengine import query
from ..errors import NotFound
from ..database import User, to_dict
from ..checks import validate_user

async def get_me():
    me = validate_user(str(request.headers.get('Authorization', '1')))

    me = to_dict(me)

    me.pop('session_ids')
    me.pop('password')

    return orjson.dumps(me)

async def get_user(user_id):
    user_id = int(user_id)
    validate_user(str(request.headers.get('Authorization', '1')))

    try:
        filtration: User = User.objects().allow_filtering()
        user = filtration.get(id=user_id)
    except(query.DoesNotExist):
        raise NotFound()

    ret = to_dict(user)

    ret.pop('session_ids')
    ret.pop('password')
    ret.pop('email')
    ret.pop('settings')

    return orjson.dumps(ret)
