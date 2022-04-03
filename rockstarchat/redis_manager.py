import redis
import os
import dotenv
import json

dotenv.load_dotenv()

pool = redis.ConnectionPool(host=os.getenv('redis_uri'), port=os.getenv('redis_port'), password=os.getenv('redis_password'), db=int(os.getenv('redis_db', 0)), retry_on_timeout=True)
manager = redis.Redis(connection_pool=pool)

def _guild_event(*, name: str, data: dict):
    _raw_data = {'t': name.upper(), 'd': data}
    manager.publish(channel='GUILD_EVENTS', message=json.dumps(_raw_data))

def _user_event(*, name: str, data: dict):
    _raw_data = {'t': name.upper(), 'd': data}
    manager.publish(channel='USER_EVENTS', message=json.dumps(_raw_data))

def guild_event(name: str, /, *, d: dict, m: bool = False) -> None:
    _guild_event(name=name, data=d, member=m)

def user_event(name: str, /, *, d: dict) -> None:
    _user_event(name=name, data=d)
