import asyncio
import base64
import os
import random
import re
import secrets
import threading
import time
from random import choice, randint
from typing import List

import bcrypt
import dotenv

EPOCH = 1649325271415  # Epoch in Milliseconds
# A bucket only lasts for 10 days, which lets us have partitions that are small and efficient
BUCKET_SIZE = 1000 * 60 * 60 * 24 * 10
dotenv.load_dotenv()

_COUNT = 0

def snowflake() -> int:
    global _COUNT
    timestamp = int(time.time() * 1000)

    ep = timestamp - EPOCH

    sflake = ep

    sflake |= (threading.current_thread().ident % 32) << 17
    sflake |= (os.getpid() % 32) << 12
    sflake |= (_COUNT % 4096)

    _COUNT += 1

    return sflake


WELCOME_MESSAGES: List[str] = [
    'Welcome, the one, the only <@{user_id}>',
    "Don'/t look away yet!, <@{user_id}> just arrived!",
    '<@{user_id}> just revived the chat :^)',
    'Coy fish, sea stakes, and more <@{user_id}> arrived!',
    'NYC Fried Pizza, Delivered by <@{user_id}>',
    "Don't cause a Discord, <@{user_id}> just arrived!",
    'I just that one game with that one character... might it be <@{user_id}>?',
    '',
]


def get_welcome_content(user_id: int) -> str:
    _msg = randint(0, len(WELCOME_MESSAGES))
    print(_msg)
    try:
        msg = WELCOME_MESSAGES[_msg]
    except:
        msg = WELCOME_MESSAGES[len(WELCOME_MESSAGES) - 1]
    return msg.format(user_id=str(user_id))


def code():
    # Generate a random, url-safe, maybe-unique token
    # TODO: Maybe check if this is a dup or not?
    _u = re.sub(
        r"\/|\+|\-|\_",
        "",
        secrets.token_urlsafe(random.randint(4, 6)),
    )
    return ''.join(choice((str.upper, str.lower))(c) for c in _u)


async def get_hash(string: str) -> str:
    loop = asyncio.get_running_loop()
    # make sure not to block the event loop
    result = await loop.run_in_executor(
        None, bcrypt.hashpw, string.encode(), bcrypt.gensalt(14)
    )
    return result.decode()


async def verify_hash(hashed_password: str, given_password: str) -> bool:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        bcrypt.checkpw,
        given_password.encode(),
        hashed_password.encode(),
    )
    return result


def get_bucket(sf: int):
    timestamp = sf >> 22
    return int(timestamp / BUCKET_SIZE)


def random_timemade():
    now = time.time_ns() // 1000000 - 1649325271415

    return base64.b32encode(str(now).encode()).decode().replace('=', '')


if __name__ == '__main__':
    # NOTE: Ignore, this is just me testing with random things

    # looks bad
    '01G0GT0D5FD779H3TYKS2B3AWD'
    # looks good
    '2124005656035328'
    '3617899005116416'
    '5796720099213312'
    # ID v2, somewhat shorter
    '1711273369'

    id = snowflake()
    print(get_bucket(id))
    print(id)
    print(len(str(id)))
    pwd = asyncio.run(get_hash('12345'))
    print(pwd)
    pwdd = asyncio.run(verify_hash(pwd, '12345'))
    print(pwdd)
