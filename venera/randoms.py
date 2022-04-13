import dotenv
import random
import re
import os
import threading
import snowflake
import secrets
from random import choice
from hashlib import sha384

EPOCH = 1649325271415 # Epoch is in GMT +8
# A bucket only lasts for 5 days, which lets us have partitions that are small and efficient
BUCKET_SIZE = 1000 * 60 * 60 * 24 * 5
dotenv.load_dotenv()

def _id() -> int:
    _generator_flake = snowflake.Generator(EPOCH, os.getpid(), threading.current_thread().ident)
    result = _generator_flake.generate()
    return result._flake

def _code():
    return str(_id())[13:].encode()

def code():
    # Generate a random, url-safe, maybe-unique token
    # TODO: Maybe check if this is a dup or not?
    _u = re.sub(r"\/|\+|\-|\_", "", secrets.token_urlsafe(random.randint(4, 6)))
    return ''.join(choice((str.upper, str.lower))(c) for c in _u)

def hashed(string: str):
    return sha384(string.encode(), usedforsecurity=True).hexdigest()

def get_bucket(sf: int):
    timestamp = sf >> 22
    return int(timestamp / BUCKET_SIZE)

if __name__ == '__main__':
    # NOTE: Ignore, this is just me testing with random things

    # looks bad
    '01G0GT0D5FD779H3TYKS2B3AWD'
    # looks good
    '2124005656035328'

    id = _id()
    print(get_bucket(id))
    print(id)
    print(len(str(id)))
    #while True:
        #print(get_bucket(id))
