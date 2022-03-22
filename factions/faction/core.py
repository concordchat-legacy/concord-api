import orjson as json
import re
from quart import Blueprint, request, Response, abort
from ..models import create_faction as make_faction, factions as db
from ..authorization import check_session

factions = Blueprint('factions', __name__)

@factions.route('', strict_slashes=False, methods=['POST'])
async def create_faction():
    creator = await check_session()

    d = await request.get_json(True)

    _name: str = d['name']

    if len(_name.split(' ')) != 1:
        raise KeyError()

    name = _name

    data = {
        'name': name,
        'description': d.get('description', ''),
        'owner_id': creator['_id'],
        'banner_url': d.get('banner_url'),
        'member_only_posting': d.get('member_only_posting', False),
        'nsfw': bool(d.get('nsfw', False))
    }

    faction = await make_faction(**data)

    return Response(json.dumps(faction), 201)

@factions.route('/<faction>', strict_slashes=False, methods=['GET'])
async def get_faction(faction):
    fact = re.compile(f'^{faction}', re.IGNORECASE)
    f = await db.find_one({'_id': fact})

    if f == None:
        return abort(404)

    return json.dumps(f), 200
