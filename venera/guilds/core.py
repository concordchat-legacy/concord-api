import orjson
from flask import request
from ..randoms import _id
from ..checks import validate_user
from ..database import Guild, Member, UserType, to_dict
from ..errors import BadData, Forbidden
from ..redis_manager import guild_event

def create_guild():
    me = validate_user(str(request.headers.get('Authorization', '1')))

    if me['bot']:
        raise Forbidden()

    guilds = Member.objects(Member.id == me['id']).all()

    if len(guilds) == 200:
        raise BadData()
    
    data: dict = request.get_json(True)
    guild_id = _id()

    inserted_data = {
        'id': guild_id,
        'name': str(data['name'])[:40],
        'description': str(data.get('description', '')),
        'owner_id': me['id'],
        'nsfw': bool(data.get('nsfw', False)),
        'perferred_locale': me['locale'],
    }

    original_member = {
        'id': me['id'],
        'guild_id': guild_id,
    }

    guild = Guild.create(**inserted_data)
    member = Member.create(**original_member, user=UserType(**dict(me)))

    guild = to_dict(guild)
    member = to_dict(member)

    guild['owner'] = member

    guild_event('GUILD_CREATE', d=guild)

    """
    first_message = Message.create(
        id=_id(),
        channel_id=channel.id,
        bucket_id=get_bucket(channel.id),
        guild_id=guild.id,
        author=UserType(**me),
        content=f'Welcome <@{me["id"]}> to your new scales guild!\nYou can customize it to your hearts content, invite your friends and more!'
    )
    """

    return orjson.dumps(guild)
