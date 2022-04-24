import secrets
import time

import dotenv
import orjson
from quart import Quart, Response, abort, jsonify

from ekranoplan.admin import admin_users
from ekranoplan.channels import channels, readstates
from ekranoplan.database import connect
from ekranoplan.errors import BadData, Err
from ekranoplan.guilds import guilds
from ekranoplan.messages import guild_msgs
from ekranoplan.randoms import snowflake
from ekranoplan.ratelimiter import limiter
from ekranoplan.users import users

try:
    import uvloop  # type: ignore

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


app = Quart('Ekranoplan')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000
app.json_encoder = ORJSONEncoder
app.json_decoder = ORJSONDecoder
limiter.init_app(app)
dotenv.load_dotenv()
connect()


@app.route('/auth/fingerprint')
async def uuid():
    return jsonify(
        {
            'fingerprint': str(snowflake())
            + '.'
            + secrets.token_urlsafe(16)
        }
    )


@app.route('/favicon.ico')
async def favicon():
    return abort(404)


@app.errorhandler(404)
async def _not_found(*args):
    return jsonify({'code': 0, 'message': '404: Not Found'})


@app.errorhandler(500)
async def _internal_error(*args):
    return jsonify(
        {'code': 0, 'message': '500: Internal Server Error'}
    )


@app.errorhandler(429)
async def _ratelimited(*args):
    return jsonify(
        {
            'retry_after': limiter.current_limit.reset_at
            - time.time(),
            'message': '429: Too Many Requests',
        }
    )


@app.errorhandler(405)
async def method_not_allowed(*args):
    return jsonify({'code': 0, 'message': '405: Method Not Allowed'})


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
        resp.headers.add(
            'X-RateLimit-Limit', limiter.current_limit.limit
        )
        resp.headers.add(
            'X-RateLimit-Remaining', limiter.current_limit.remaining
        )
        resp.headers.add(
            'X-RateLimit-Reset', limiter.current_limit.reset_at
        )
        resp.headers.add(
            'X-RateLimit-Reset-After',
            limiter.current_limit.reset_at - int(time.time()),
        )
    return resp


bps = {
    admin_users: '/admin/users',
    users: '/users',
    guilds: '/guilds',
    guild_msgs: '/guilds',
    channels: -1,
    readstates: -1
}

for bp, url in bps.items():
    url_prefix = url if url != -1 else ''
    app.register_blueprint(bp, url_prefix=url_prefix)

if __name__ == '__main__':
    app.run(debug=True)
