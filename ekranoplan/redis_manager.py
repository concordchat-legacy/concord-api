import os

import aioredis as redis
import dotenv
import orjson

dotenv.load_dotenv()

pool = redis.ConnectionPool(
    host=os.getenv('redis_uri'),
    port=os.getenv('redis_port'),
    password=os.getenv('redis_password'),
    db=int(os.getenv('redis_db', 0)),
    retry_on_timeout=True,
)

if os.name != 'nt':
    pool.connection_class = redis.UnixDomainSocketConnection

manager = redis.Redis(connection_pool=pool)

# Possible Types
# 1: User(s)
# 2: Guild(s)
# 3: Channel(s)
# 4: ???
# 5: Friend Request(s)
# 6: Member(s)
# 7: Presence


async def user_event(name: str, user_id: int, data: dict):
    d = {'type': 1, 'name': name, 'user_id': user_id, 'data': data}

    await manager.publish('gateway', orjson.dumps(d))


async def guild_event(name: str, guild_id: int, data: dict, user_id: int = None):
    d = {
        'type': 2,
        'name': name,
        'guild_id': guild_id,
        'user_id': user_id,
        'data': data,
    }

    await manager.publish('gateway', orjson.dumps(d))


async def channel_event(name: str, channel: dict, data: dict, guild_id: int = None, is_message: bool = False):
    d = {
        'type': 3,
        'name': name,
        'channel': channel,
        'guild_id': guild_id,
        'data': data,
        'is_message': is_message
    }

    await manager.publish('gateway', orjson.dumps(d))


async def friend_request_event(name: str, user_id: int, data: dict):
    d = {'type': 5, 'name': name, 'requester_id': user_id, 'data': data}

    await manager.publish('gateway', orjson.dumps(d))


async def member_event(name: str, member_id: int, data: dict):
    d = {'type': 6, 'name': name, 'member_id': member_id, 'data': data}

    await manager.publish('gateway', orjson.dumps(d))


async def presence_event(name: str, user_id: int, data: dict):
    d = {'type': 7, 'name': name, 'user_id': user_id, 'data': data}

    await manager.publish('gateway', orjson.dumps(d))
