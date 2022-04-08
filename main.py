import multiprocessing
import os
import threading
import orjson
import logging
import sys
from flask import Flask, Response, send_file
from rockstarchat.ratelimiter import limiter
from rockstarchat.randoms import _id, code
from rockstarchat.errors import Err, BadData
from rockstarchat.admin import bp as admin_users
from rockstarchat.users import bp as users
from rockstarchat.guilds import bp as guilds
from rockstarchat.channels import bp as channels

try:
    import uvloop # type: ignore
    uvloop.install()
except:
    pass

app = Flask('Scales')
limiter.init_app(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/__development/ping')
async def ping():
    return orjson.dumps({'cookie': 'pong!'})

@app.route('/__development/uuid')
async def uuid():
    return orjson.dumps({'id': str(_id())})

@app.route('/__development/u-id')
async def s_id():
    return orjson.dumps({'id': code()})

@app.route('/favicon.ico')
async def _get_icon():
    try:
        return send_file(os.path.join(app.root_path, 'static', 'favicon.ico'), 'image/vnd.microsoft.icon')
    except FileNotFoundError:
        return send_file(os.path.join(app.root_path, 'rockstarchat', 'static', 'favicon.ico'), 'image/vnd.microsoft.icon')

@app.errorhandler(404)
async def _not_found(*args):
    return orjson.dumps({'code': 0, 'message': '404: Not Found'})

@app.errorhandler(500)
async def _internal_error(*args):
    return orjson.dumps({'code': 0, 'message': '500: Internal Server Error'})

@app.errorhandler(429)
async def _ratelimited(*args):
    return orjson.dumps({'code': 0, 'message': '429: Too Many Requests'})

#@app.errorhandler(KeyError)
#async def _bad_data(*args):
    #b = BadData()
    #return b._to_json(), 403

@app.errorhandler(Err)
async def _default_error_handler(err: Err):
    return err._to_json(), err.resp_type

@app.after_request
async def _after_request(resp: Response):
    resp.headers['content_type'] = 'application/json'
    resp.headers.remove('Retry-After')
    try:
        app.logger.debug(resp.status, resp.get_data(), threading.current_thread().ident, multiprocessing.current_process().ident, file=sys.stderr)
    except:
        pass
    return resp

bps = {
    admin_users: '/__development/admin/users',
    users: '/users',
    guilds: '/guilds',
    channels: '/'
}

for bp, url in bps.items():
    app.register_blueprint(bp, url_prefix=url)

if __name__ == '__main__':
    app.run(debug=True)
