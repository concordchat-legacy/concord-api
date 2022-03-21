import json
import quart
import logging
import os
import hypercorn
from .db import loop, index
from .errors import Error
from .ratelimiter import limiter
from .faction.core import factions
from .users.core import users
from .randoms import snowflake, code

app = quart.Quart(__name__)
app.config['debug'] = True
logging.basicConfig(level=logging.DEBUG)
limiter.init_app(app)

@app.errorhandler(Error)
async def error_handle(err: Error):
    return quart.Response(err._as_json(), err.status_code)

@app.errorhandler(KeyError)
async def invalid_data(err: KeyError):
    return json.dumps({'message': '400: Invalid Data','code': 0})

@app.errorhandler(404)
async def not_found(*_):
    return json.dumps({'message': '404: Not Found', 'code': 0})

@app.errorhandler(500)
async def internal_server_error(err):
    print(err)
    return json.dumps({'message': '500: Internal Server Error', 'code': 0})

@app.get('/codes/snowflake')
async def create_snowflake():
    return json.dumps({'_id': snowflake()})

@app.get('/codes/invites')
async def create_invite_code():
    return json.dumps({'_id': code()})

@app.after_request
async def after_request(resp: quart.Response):
    msg = f'Responded to {quart.request.remote_addr} with {await resp.get_data(True)}'
    print(f'DEBUG:core:{msg}')
    return resp

cfg = hypercorn.config.Config()
cfg.bind.clear()
cfg.bind.append(f'0.0.0.0:{os.getenv("PORT")}')

bps: dict[quart.Blueprint, str] = {
    factions: '/factions',
    users: '/users',
}

for k, v in bps.items():
    app.register_blueprint(k, url_prefix=v)

loop.create_task(index())
loop.run_until_complete(hypercorn.asyncio.serve(app, cfg))
loop.run_forever()