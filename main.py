import orjson
import logging
import time
from flask import Flask, Response, jsonify
from concord.ratelimiter import limiter
from concord.randoms import snowflake
from concord.errors import Err, BadData
from concord.admin import bp as admin_users
from concord.users import bp as users
from concord.guilds import bp as guilds
from concord.channels import bp as channels

try:
    import uvloop # type: ignore
    uvloop.install()
except:
    pass

class ORJSONDecoder:
    def __init__(self, **kwargs):
        self.options = kwargs

    def decode(self, obj):
        return orjson.loads(obj)


class ORJSONEncoder:
    def __init__(self, **kwargs):
        self.options = kwargs

    def encode(self, obj):
        return orjson.dumps(obj).decode('utf-8')

app = Flask('concore')
app.json_encoder = ORJSONEncoder
app.json_decoder = ORJSONDecoder
limiter.init_app(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/auth/fingerprint?version=1')
async def uuid():
    return jsonify({'id': str(snowflake())})

@app.errorhandler(404)
async def _not_found(*args):
    return jsonify({'code': 0, 'message': '404: Not Found'})

@app.errorhandler(500)
async def _internal_error(*args):
    return jsonify({'code': 0, 'message': '500: Internal Server Error'})

@app.errorhandler(429)
async def _ratelimited(*args):
    return jsonify({'code': 0, 'message': '429: Too Many Requests'})

@app.errorhandler(KeyError)
async def _bad_data(*args):
    b = BadData()
    return b._to_json(), 403

@app.errorhandler(Err)
async def _default_error_handler(err: Err):
    return err._to_json(), err.resp_type

@app.after_request
async def _after_request(resp: Response):
    if limiter.current_limit:
        resp.headers.add('X-RateLimit-Limit', limiter.current_limit.limit)
        resp.headers.add('X-RateLimit-Remaining', limiter.current_limit.remaining)
        resp.headers.add('X-RateLimit-Reset', limiter.current_limit.reset_at)
        resp.headers.add('X-RateLimit-Reset-After', int(time.time()) - limiter.current_limit.reset_at)
        resp.headers.add('X-RateLimit-Bucket', limiter._key_func())
    return resp

bps = {
    admin_users: '/__development/admin/users',
    users: '/users',
    guilds: '/guilds',
    channels: -1
}

for bp, url in bps.items():
    url_prefix = url if url != -1 else ''
    app.register_blueprint(bp, url_prefix=url_prefix)

if __name__ == '__main__':
    app.run(debug=True)
