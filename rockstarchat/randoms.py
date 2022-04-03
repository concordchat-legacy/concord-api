from time import time
import dotenv
import base64
import re
import os
import threading
import snowflake
from random import choice
from hashlib import sha384

dotenv.load_dotenv()
_generator_flake = snowflake.Generator(1648953594118, os.getpid(), threading.current_thread().ident)

def _id() -> str:
    result = _generator_flake.generate()
    return str(result)

def _code():
    return _id()[:5].encode()

def code():
    _u = re.sub(r"\/|\+|\-|\_", "", base64.b64encode(_code()).decode('ascii').strip('==='))
    return ''.join(choice((str.upper, str.lower))(c) for c in _u)

def hashed(string: str):
    return sha384(string.encode()).hexdigest()

if __name__ == '__main__':
    print(code())
    print(hashed(code()))
    while True:
        print(_id())