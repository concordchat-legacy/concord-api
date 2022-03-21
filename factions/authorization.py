from quart import request
from .db import users
from .errors import Forbidden

async def check_session() -> dict:
    r = await users.find_one({'session_ids': [request.headers.get('Authorization', '')]})
    
    if r == None:
        raise Forbidden()
    
    return r
