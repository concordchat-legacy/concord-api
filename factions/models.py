from .db import factions, users, members
from .errors import Forbidden

async def create_faction(
    name: str,
    description: str,
    owner_id: str,
    member_only_posting: bool,
    banner_url: str = None,
    nsfw: bool = False,
):
    f = await factions.find_one({'_id': name})

    if f != None:
        raise Forbidden('Faction name is already taken')

    data = {
        '_id': name,
        'description': description,
        'owner_id': owner_id,
        'banner_url': banner_url or '',
        'flags': 1 << 1,
        'nsfw': nsfw,
        'member_only_posting': member_only_posting,
    }

    user = await users.find_one({'_id': owner_id})

    user.pop('email')
    user.pop('password')
    user.pop('session_ids')
    user.pop('blocked_users')

    member = {
        'id': user['_id'],
        'user': user,
        'faction': name,
        'moderator': True,
        'owner': True
    }

    m, d, = member.copy(), data.copy()

    await members.insert_one(member)
    await factions.insert_one(data)

    ret = {
        'faction': d,
        'you': m,
    }

    return ret
