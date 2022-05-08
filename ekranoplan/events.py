# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
import os

import dotenv
import orjson
from kafka import KafkaProducer

dotenv.load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_HOSTS'),
    security_protocol='SASL_SSL',
    sasl_mechanism='PLAIN',
    sasl_plain_username=os.getenv('KAFKA_USERNAME'),
    sasl_plain_password=os.getenv('KAFKA_PASSWORD'),
)

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

    producer.send('users', orjson.dumps(d))


async def guild_event(name: str, guild_id: int, data: dict, user_id: int = None):
    d = {
        'type': 2,
        'name': name,
        'guild_id': guild_id,
        'user_id': user_id,
        'data': data,
    }

    producer.send('guilds', orjson.dumps(d))


async def channel_event(
    name: str,
    channel: dict,
    data: dict,
    guild_id: int = None,
    is_message: bool = False,
):
    d = {
        'type': 3,
        'name': name,
        'channel': channel,
        'guild_id': guild_id,
        'data': data,
        'is_message': is_message,
    }

    producer.send('channels', orjson.dumps(d))


async def friend_request_event(name: str, user_id: int, receiver_id: int, data: dict):
    d = {
        'type': 5,
        'name': name,
        'requester_id': user_id,
        'receiver_id': receiver_id,
        'data': data,
    }

    producer.send('friends', orjson.dumps(d))


async def member_event(name: str, member_id: int, guild_id: int, data: dict):
    d = {
        'type': 6,
        'name': name,
        'member_id': member_id,
        'guild_id': guild_id,
        'data': data,
    }

    await producer.send('members', orjson.dumps(d))


async def presence_event(name: str, user_id: int, data: dict):
    d = {'type': 7, 'name': name, 'user_id': user_id, 'data': data}

    await producer.send('presences', orjson.dumps(d))
