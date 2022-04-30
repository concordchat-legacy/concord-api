import secrets
import traceback

import dotenv
from blacksheep import Application, not_found
from blacksheep.exceptions import (
    BadRequest,
    BadRequestFormat,
    InternalServerError,
    InvalidArgument,
    NotFound,
)
from blacksheep_prometheus import PrometheusMiddleware, metrics
from cassandra.cqlengine.query import DoesNotExist

from ekranoplan.admin import admin_users
from ekranoplan.channels import channels, readstates
from ekranoplan.database import Guild, GuildInvite, connect, to_dict
from ekranoplan.errors import BadData, Err, NotFound
from ekranoplan.guilds import guilds, members
from ekranoplan.messages import guild_messages
from ekranoplan.randoms import factory
from ekranoplan.users import users
from ekranoplan.utils import jsonify

try:
    import uvloop  # type: ignore

    uvloop.install()
except:
    pass

app = Application(show_error_details=True, debug=True)
dotenv.load_dotenv()


@app.route('/auth/fingerprint')
async def uuid():
    return jsonify(
        {'fingerprint': str(factory().formulate()) + '.' + secrets.token_urlsafe(16)}
    )


@app.route('/favicon.ico')
async def favicon():
    return not_found('Favicon is not provided by Ekranoplan')


@app.route('/invites/{str:invite_code}', methods=['GET'])
async def get_guild_by_invite(invite_code: str):
    try:
        invite: GuildInvite = GuildInvite.objects(GuildInvite.id == invite_code.lower()).get()
    except (DoesNotExist):
        raise NotFound()

    guild: Guild = Guild.objects(Guild.id == invite.guild_id).get()

    return jsonify(to_dict(guild))


@app.on_start
async def on_start(application: Application):
    app.middlewares.append(
        PrometheusMiddleware(
            'total_requests',
            'total_responses',
            'avg_request_time',
            'exceptions',
            'requests_in_progress',
        )
    )
    app.router.add_get('/metrics', metrics)
    connect()


async def _bad_data(app, req, err: Exception):
    b = BadData()
    r = b._to_json()
    r.status = 400
    print(traceback.print_exc())
    return r


async def _default_error_handler(app, req, err: Err):
    r = err._to_json()
    r.status = err.resp_type
    print(traceback.print_exc())
    return r


async def _internal_server_err(app, req, err: Exception):
    print(traceback.print_exc())
    return jsonify({'code': 0, 'message': '500: Internal Server Error'}, 500)


async def _not_found(app, req, err: Exception):
    print(traceback.print_exc())
    return jsonify({'code': 0, 'message': '404: Not Found'}, 404)


app.exceptions_handlers.update(
    {
        Err: _default_error_handler,
        KeyError: _bad_data,
        InvalidArgument: _bad_data,
        InternalServerError: _internal_server_err,
        NotFound: _not_found,
        ValueError: _bad_data,
        TypeError: _bad_data,
        BadRequest: _bad_data,
        BadRequestFormat: _bad_data,
        DoesNotExist: _bad_data,
    }
)

bps = [
    admin_users,
    users,
    guilds,
    guild_messages,
    channels,
    readstates,
    members,
]

app.register_controllers(bps)
