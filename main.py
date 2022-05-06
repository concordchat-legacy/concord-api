# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
import secrets
import traceback

import dotenv
import orjson
from blacksheep import Application, Request, not_found
from blacksheep.exceptions import (
    BadRequest,
    BadRequestFormat,
    InternalServerError,
    InvalidArgument,
    NotFound,
)
from blacksheep_prometheus import PrometheusMiddleware, metrics
from cassandra.cqlengine.query import DoesNotExist
from email_validator import EmailSyntaxError

from ekranoplan.public import public
from ekranoplan.admin import admin_users
from ekranoplan.channels import channels, readstates
from ekranoplan.checks import add_guild_meta, audit, validate_user
from ekranoplan.database import Guild, GuildInvite, Member, connect, to_dict
from ekranoplan.errors import BadData, Conflict, Err, Forbidden, NotFound
from ekranoplan.guilds import audits, guilds, members
from ekranoplan.messages import guild_messages
from ekranoplan.randoms import factory
from ekranoplan.events import member_event
from ekranoplan.users import meta, users
from ekranoplan.utils import jsonify

try:
    import uvloop  # type: ignore

    uvloop.install()
except:
    pass

app = Application(show_error_details=False, debug=True)
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
async def get_guild_by_invite(invite_code: str, request: Request):
    try:
        invite: GuildInvite = GuildInvite.objects(
            GuildInvite.id == invite_code.lower()
        ).get()
    except (DoesNotExist):
        raise NotFound()

    data = await request.json(orjson.loads)

    if data is not None:
        accept = bool(data.get('accept', False))
    else:
        accept = False

    guild: Guild = Guild.objects(Guild.id == invite.guild_id).get()

    if not accept:
        return jsonify(to_dict(guild))

    auth = request.get_single_header(b'Authorization').decode()

    me = validate_user(auth, stop_bots=True)

    mems = Member.objects(Member.id == me.id).all()

    if len(mems) == 300:
        raise Forbidden()

    try:
        Member.objects(Member.id == me.id, Member.guild_id == guild.id).get()
    except:
        pass
    else:
        raise Conflict()

    member: Member = Member.create(id=me.id, guild_id=guild.id)
    add_guild_meta(me.id, guild.id)

    await member_event('JOIN', member.id, guild_id=guild.id, data=to_dict(member))

    audit(
        'MEMBER_JOIN',
        guild_id=guild.id,
        postmortem=f'# User `{me.username}/{str(member.id)}` Joined `{guild.name}`/`{str(guild.id)}` At `{str(member.joined_at)}`\n\n- Using `{invite_code}`',
        audited=member.id,
        object_id=member.id,
    )

    return jsonify(to_dict(member))


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


async def email_err(app, req, err: Exception):
    return jsonify({'code': 'email_validation_error', 'message': f'{str(err)}'})


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
        EmailSyntaxError: email_err,
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
    meta,
    audits,
    public,
]

app.register_controllers(bps)
