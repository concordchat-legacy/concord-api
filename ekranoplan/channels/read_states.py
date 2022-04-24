from cassandra.cqlengine.query import DoesNotExist
from quart import Blueprint, jsonify, request

from ..checks import search_messages, validate_channel, validate_user
from ..database import Channel, Message, ReadState, to_dict
from ..errors import BadData, NotFound

bp = Blueprint('readstates', __name__)


@bp.route(
    '/channels/<int:channel_id>/messages/<int:message_id>/ack',
    methods=['POST'],
    strict_slashes=False,
)
async def ack_message(channel_id: int, message_id: int):
    user_id = validate_user(
        request.headers.get('Authorization'), stop_bots=True
    ).id

    try:
        Channel.objects(Channel.id == channel_id).get()
    except (DoesNotExist):
        raise NotFound()

    message = search_messages(
        channel_id=channel_id, message_id=message_id
    )

    if message is None:
        raise BadData()

    try:
        read_state: ReadState = ReadState.objects(
            ReadState.user_id == user_id,
            ReadState.channel_id == channel_id,
        ).get()
    except (DoesNotExist):
        read_state: ReadState = ReadState.create(
            user_id=user_id, channel_id=channel_id
        )

    read_state.last_message_id = message.id

    read_state = read_state.save()

    return jsonify(to_dict(read_state))


@bp.route(
    '/channels/<int:channel_id>/readstate', strict_slashes=False
)
async def get_channel_read_state(channel_id: int):
    user_id = validate_user(
        request.headers.get('Authorization'), stop_bots=True
    ).id

    try:
        Channel.objects(Channel.id == channel_id).get()
    except (DoesNotExist):
        raise BadData()

    try:
        obj = ReadState.objects(
            ReadState.user_id == user_id,
            ReadState.channel_id == channel_id,
        ).get()
    except (DoesNotExist):
        raise NotFound()

    return jsonify(to_dict(obj))


@bp.route(
    '/guilds/<int:guild_id>/channels/<int:channel_id>/messages/<int:message_id>/ack',
    methods=['POST'],
    strict_slashes=False,
)
async def ack_guild_message(
    guild_id: int, channel_id: int, message_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='read_message_history',
        stop_bots=True,
    )

    message = search_messages(
        channel_id=channel_id, message_id=message_id
    )

    if message is None:
        raise BadData()

    try:
        read_state: ReadState = ReadState.objects(
            ReadState.user_id == user.id,
            ReadState.channel_id == channel_id,
        ).get()
    except (DoesNotExist):
        read_state: ReadState = ReadState.create(
            user_id=user.id, channel_id=channel_id
        )

    read_state.last_message_id = message.id

    read_state = read_state.save()

    return jsonify(to_dict(read_state))


@bp.route(
    '/guilds/<int:guild_id>/channels/<int:channel_id>',
    strict_slashes=False,
)
async def get_guild_channel_read_state(
    guild_id: int, channel_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='read_message_history',
        stop_bots=True,
    )

    try:
        obj = ReadState.objects(
            ReadState.user_id == user.id,
            ReadState.channel_id == channel_id,
        ).get()
    except (DoesNotExist):
        raise NotFound()

    return jsonify(to_dict(obj))


@bp.route('/readstates')
async def get_readstates():
    me = validate_user(
        request.headers.get('Authorization'), stop_bots=True
    )

    _readstates = ReadState.objects(ReadState.user_id == me.id).all()

    readstates = []

    for readstate in _readstates:
        readstates.append(to_dict(readstate))

    return jsonify(readstates)
