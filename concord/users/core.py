from quart import request, jsonify
from cassandra.cqlengine import query
from ..errors import NotFound
from ..database import User, to_dict
from ..checks import validate_user

async def get_me():
    me = validate_user(str(request.headers.get('Authorization', '1')))

    me = to_dict(me)

    me.pop('password')

    return jsonify(me)

async def get_user(user_id):
    user_id = int(user_id)
    validate_user(str(request.headers.get('Authorization', '1')))

    try:
        user: User = User.objects(User.id == user_id).get()
    except(query.DoesNotExist):
        raise NotFound()

    ret = to_dict(user)

    ret.pop('password')
    ret.pop('email')
    ret.pop('settings')

    return jsonify(ret)
