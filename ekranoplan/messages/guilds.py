from quart import Blueprint, jsonify, request

from ..checks import search_messages, validate_channel
from ..database import Message, GuildChannelPin, _get_date, to_dict
from ..errors import BadData, Forbidden
from ..randoms import get_bucket, snowflake

bp = Blueprint('guild-messages', __name__)


@bp.get(
    '/<int:guild_id>/channels/<int:channel_id>/messages/<int:message_id>',
    strict_slashes=False,
)
async def get_guild_channel_message(
    guild_id: int, channel_id: int, message_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='read_message_history',
    )

    msg = search_messages(
        channel_id=channel.id, message_id=message_id
    )

    return jsonify(to_dict(msg))


@bp.get(
    '/<int:guild_id>/channels/<int:channel_id>/messages',
    strict_slashes=False,
)
async def get_guild_channel_messages(guild_id: int, channel_id: int):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='read_message_history',
    )

    limit = int(request.args.get('limit', 50))

    if limit > 10000:
        raise BadData()

    _msgs = search_messages(channel_id=channel.id, limit=limit)
    msgs = []

    for msg in _msgs:
        msgs.append(to_dict(msg))

    return jsonify(msgs)


@bp.post(
    '/<int:guild_id>/channels/<int:channel_id>/messages',
    strict_slashes=False,
)
async def create_guild_channel_message(
    guild_id: int, channel_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='send_messages',
    )

    d: dict = await request.get_json()

    if '@everyone' in d['content']:
        mentions_everyone = True if perms.mention_everyone else False
    else:
        mentions_everyone = False

    if d.get('referenced_message_id'):
        referenced_message = search_messages(
            channel_id=channel_id,
            message_id=int(d.pop('referenced_message_id')),
        )

    if referenced_message is None:
        raise BadData()

    data = {
        'id': snowflake(),
        'channel_id': channel_id,
        'bucket_id': get_bucket(channel_id),
        'guild_id': guild_id,
        'author': member.user,
        'content': str(d['content']),
        'mentions_everyone': mentions_everyone,
        'referenced_message_id': referenced_message.id,
    }

    msg = Message.create(**data)

    return jsonify(to_dict(msg))


@bp.patch(
    '/<int:guild_id>/channels/<int:channel_id>/messages/<int:message_id>',
    strict_slashes=False,
)
async def edit_guild_channel_message(
    guild_id: int, channel_id: int, message_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission=None,
    )

    msg = search_messages(
        channel_id=channel.id, message_id=message_id
    )

    if msg is None:
        raise BadData()

    if msg.author.id != member.id:
        raise Forbidden()

    d: dict = await request.get_json()

    if d.get('content'):
        msg.content = str(d.pop('content'))

    msg.last_edited = _get_date()

    msg = msg.save()

    return jsonify(to_dict(msg))


@bp.delete(
    '/<int:guild_id>/channels/<int:channel_id>/messages/<int:message_id>',
    strict_slashes=False,
)
async def delete_guild_channel_message(
    guild_id: int, channel_id: int, message_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='manage_messages',
    )

    msg = search_messages(
        channel_id=channel.id, message_id=message_id
    )

    if msg is None:
        raise BadData()

    msg.delete()

    r = jsonify([])
    r.status_code = 204

    return r

@bp.post(
    '/<int:guild_id>/channels/<int:channel_id>/pins/<int:message_id>',
    strict_slashes=False
)
async def pin_guild_channel_message(
    guild_id: int, channel_id: int, message_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='manage_channel_pins',
    )

    msg = search_messages(channel_id=channel.id, message_id=message_id)

    if msg is None:
        raise BadData()

    msg.pinned = True

    possibly_not_empty = GuildChannelPin.objects(
        GuildChannelPin.channel_id == channel_id,
        GuildChannelPin.message_id == message_id
    )

    if possibly_not_empty.all() != []:
        raise BadData()

    pin = GuildChannelPin.create(
        channel_id=channel_id,
        message_id=message_id
    )
    msg = msg.save()

    ret = {
        'pinned_data': to_dict(pin),
        'message_pinned': to_dict(msg)
    }

    return jsonify(ret)

@bp.delete(
    '/<int:guild_id>/channels/<int:channel_id>/pins/<int:message_id>',
    strict_slashes=False,
)
async def unpin_guild_channel_message(
    guild_id: int, channel_id: int, message_id: int
):
    member, user, channel, perms = validate_channel(
        token=request.headers.get('Authorization'),
        guild_id=guild_id,
        channel_id=channel_id,
        permission='manage_channel_pins',
    )

    msg = search_messages(channel_id=channel.id, message_id=message_id)

    if msg is None or not msg.pinned:
        raise BadData()

    msg.pinned = False
    pin: GuildChannelPin = GuildChannelPin.objects(
        GuildChannelPin.channel_id == channel_id,
        GuildChannelPin.message_id == message_id
    ).get()
    pin.delete()
    msg.save()

    r = jsonify([])
    r.status_code = 204

    return jsonify(r)
