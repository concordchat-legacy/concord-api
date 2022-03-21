import dotenv
import os
import base64
import re
import time
import snowflake as _snowflake
from random import choice
from hashlib import sha384

dotenv.load_dotenv()
Snowflake = str
generator = _snowflake.Generator(1448841601000, int(os.getenv('process_id', 0)), int(os.getenv('worker_id', 0)))

def snowflake():
    return str(generator.generate(int(round(time.time() * 1000))))

def _code():
    return snowflake()[13:].encode()

def code():
    _u = re.sub(r"\/|\+|\-|\_", "", base64.b64encode(_code()).decode('ascii').strip('==='))
    return ''.join(choice((str.upper, str.lower))(c) for c in _u)

def hashed(string: str):
    return sha384(string.encode()).hexdigest()
