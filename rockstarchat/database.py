import os
import pymongo
import uuid
import datetime
from dotenv import load_dotenv
from typing import Any, Union

load_dotenv()

mongodb = pymongo.MongoClient(os.getenv('mongo_uri'))

def create_user(
    id: int,
    username: str,
    discriminator: int,
    email: str,
    password: str,
    system: bool = False,
    verified: bool = False,
    locale: str = 'EN_US/EU',
    flags: int = 1 << 0,
    avatar: str = '',
    banner: str = '',
    bot: bool = False,
    bio: str = '',
    settings: dict = {'accept_friend_requests': True, 'accept_dms': True},
    joined_at: str = datetime.datetime.now().isoformat()
):
    kwargs = {}
    kwargs['_id'] = id
    kwargs['username'] = username
    kwargs['discriminator'] = discriminator
    kwargs['bio'] = bio
    kwargs['email'] = email
    kwargs['password'] = password
    kwargs['joined_at'] = joined_at
    kwargs['system'] = system
    kwargs['verified'] = verified
    kwargs['locale'] = locale
    kwargs['flags'] = flags
    kwargs['avatar'] = avatar
    kwargs['banner'] = banner
    kwargs['bot'] = bot
    kwargs['session_ids'] = [uuid.uuid1()]
    kwargs['settings'] = settings
    mongodb.get_database('users').get_collection('profiles').insert_one(kwargs)
    return kwargs

def get_user_by(key: Union[int, str]):
    if isinstance(key, int):
        result = mongodb.get_database('users').get_collection('profiles').find_one({'_id': key})
        result['id'] = result.pop('_id')
        return result
    elif isinstance(key, str):
        result = mongodb.get_database('users').get_collection('profiles').find_one({'session_ids': key})
        result['id'] = result.pop('_id')

def migrate(db: str, col: str, key: str, value: Any = None, delete: bool = False):
    query = mongodb.get_database(db).get_collection(col).find()
    for doc in query:
        if delete:
            if doc.get('key') is not None:
                mongodb.get_database(db).get_collection(col).update_many({}, {'$unset': key})
        else:
            mongodb.get_database(db).get_collection(col).update_many({}, {key: value})

# TODO: Change default permission
def create_guild(
    id: int,
    name: str,
    owner_id: int,
    nsfw: bool = False,
    large: bool = False,
    perferred_locale: str = 'EN_US/EU',
    permissions: str = 0,
    vanity_url: str = None,
    splash: str = '',
    icon: str = '',
    banner: str = '',
    description: str = '',
):
    kwargs = {}
    kwargs['_id'] = id
    kwargs['name'] = name
    kwargs['description'] = description
    kwargs['vanity_url'] = vanity_url
    kwargs['icon'] = icon
    kwargs['banner'] = banner
    kwargs['owner_id'] = owner_id
    kwargs['nsfw'] = nsfw
    kwargs['large'] = large
    kwargs['perferred_locale'] = perferred_locale
    kwargs['permissions'] = permissions
    kwargs['splash'] = splash
    mongodb.get_database('guilds').get_collection('information').insert_one(kwargs)
    return kwargs

def get_guild(id: int):
    result = mongodb.get_database('guilds').get_collection('information').find_one({'_id': id})
    result['id'] = result.pop('_id')
    return result

def create_member(user: dict, guild_id: int):
    kwargs = {}
    kwargs['_id'] = uuid.uuid1()
    kwargs['user_id'] = user['id']
    kwargs['user'] = user
    kwargs['guild_id'] = guild_id
    kwargs['joined_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    kwargs['roles'] = []
    kwargs['nick'] = ''
    kwargs['permissions'] = 0
    kwargs['custom_color'] = 0
    kwargs['avatar'] = ''
    kwargs['banner'] = ''
    mongodb.get_database('guilds').get_collection('members').insert_one(kwargs)
    return kwargs

def get_member(user_id: int, guild_id: int) -> dict:
    result = mongodb.get_database('guilds').get_collection('members').find_one({'user_id': user_id, 'guild_id': guild_id})
    result.pop('_id')
    return result

def create_role(
    id: int,
    guild_id: int,
    name: str,
    position: int,
    color: int = 0,
    hoist: bool = False,
    icon: str = '',
    permissions: int = 0,
    mentionable: bool = False,
):
    kwargs = {}
    kwargs['_id'] = id
    kwargs['guild_id'] = guild_id
    kwargs['name'] = name
    kwargs['position'] = position
    kwargs['color'] = color
    kwargs['hoist'] = hoist
    kwargs['icon'] = icon
    kwargs['permissions'] = permissions
    kwargs['mentionable'] = mentionable
    kwargs['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    mongodb.get_database('guilds').get_collection('roles').insert_one(kwargs)
    return kwargs

def get_role(id: int):
    result = mongodb.get_database('guilds').get_collection('roles').find_one({'_id': id})
    result['id'] = result.pop('_id')
    return result

def _initiate_all():
    g = mongodb.get_database('guilds')
    u = mongodb.get_database('users')
    p = u.get_collection('profiles')
    m = g.get_collection('members')
    r = g.get_collection('roles')
    i = g.get_collection('information')

    m.create_index([('user_id', pymongo.ASCENDING)])
    m.create_index('guild_id')

    i.create_index(['owner_id', 'vanity_url'])

    p.create_index('bot')

    r.create_index('user_id')
    r.create_index('guild_id')

if __name__ == '__main__':
    _initiate_all()
