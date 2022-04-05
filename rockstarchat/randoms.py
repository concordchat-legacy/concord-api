import dotenv
import random
import re
import os
import threading
import snowflake
import secrets
from random import choice
from hashlib import sha384

EPOCH = 1417276802000
BUCKET_SIZE = 1000 * 60 * 60 * 24 * 10
dotenv.load_dotenv()

def _id() -> int:
    _generator_flake = snowflake.Generator(EPOCH, os.getpid(), threading.current_thread().ident)
    result = _generator_flake.generate()
    return result._flake

def _code():
    return str(_id())[13:].encode()

def code():
    _u = re.sub(r"\/|\+|\-|\_", "", secrets.token_urlsafe(random.randint(4, 6)))
    return ''.join(choice((str.upper, str.lower))(c) for c in _u)

def hashed(string: str):
    return sha384(string.encode(), usedforsecurity=True).hexdigest()

def get_bucket(sf: int):
    timestamp = snowflake.Snowflake(EPOCH, sf).timestamp
    return int(timestamp / BUCKET_SIZE)

if __name__ == '__main__':
    id = _id()
    #while True:
        #print(get_bucket(id))
