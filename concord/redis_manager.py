import os

import dotenv
import orjson
import aioredis as redis

dotenv.load_dotenv()

pool = redis.ConnectionPool(
    host=os.getenv('redis_uri'),
    port=os.getenv('redis_port'),
    password=os.getenv('redis_password'),
    db=int(os.getenv('redis_db', 0)),
    retry_on_timeout=True,
)
manager = redis.Redis(connection_pool=pool)


async def _guild_event(*, name: str, data: dict, member=None, presence=False):
    # TODO: Redo this data structure, it's honestly messsy asf
    _raw_data = {
        't': name.upper(),
        'd': data,
        'member_id': member,
        'presence': presence,
    }
    await manager.publish(channel='GUILD_EVENTS', message=orjson.dumps(_raw_data).decode())


async def _user_event(*, name: str, data: dict):
    _raw_data = {'t': name.upper(), 'd': data}
    await manager.publish(channel='USER_EVENTS', message=orjson.dumps(_raw_data).decode())


async def guild_event(name: str, /, *, d: dict, m: bool = False, p: bool = False) -> None:
    await _guild_event(name=name, data=d, member=m, presence=p)


async def user_event(name: str, /, *, d: dict) -> None:
    await _user_event(name=name, data=d)
