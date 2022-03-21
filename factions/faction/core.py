import json
from quart import Blueprint, request, Response
from ..models import create_faction as make_faction
from ..authorization import check_session

factions = Blueprint('factions', __name__)

@factions.post('', strict_slashes=False)
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
