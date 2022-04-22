from quart import Blueprint, jsonify, request

from ..checks import (
    validate_channel,
    validate_member,
    verify_channel_position,
    verify_parent_id,
)
from ..database import Guild, GuildChannel, Role, to_dict
from ..errors import BadData, Forbidden, NotFound
from ..flags import GuildPermissions
from ..randoms import snowflake
from ..redis_manager import guild_event

bp = Blueprint('channels', __name__)


@bp.route('/guilds/<int:guild_id>/channels', strict_slashes=False, methods=['POST'])
async def create_channel(guild_id: int):
    guild: Guild = Guild.objects(Guild.id == guild_id).first()

    if guild == None:
        raise NotFound()

    member, me = validate_member(request.headers.get('Authorization', '1'), guild_id)
    me = to_dict(me)
    me.pop('email')
    me.pop('password')
    me.pop('settings')

    permissions = None

    if member.roles == []:
        permissions = guild.permissions
    else:
        id = member.roles[0]

        role: Role = Role.objects(Role.id == id, Role.guild_id == guild_id).get()

        permissions = role.permissions

    calc = GuildPermissions(permissions)

    if (
        not calc.manage_channels
        and member.id != guild.owner_id
        and not calc.administator
    ):
        raise Forbidden()

    data: dict = request.get_json(True)

    slowmode = 0

    if data.get('slowmode_timeout'):
        if int(data.get('slowmode_timeout')) > 21600 or data.get('slowmode') < 0:
            raise BadData()
        else:
            slowmode = round(int(data.pop('slowmode_timeout')))

    if int(data.get('type')) not in [0, 1]:
        raise BadData()

    if data.get('parent_id'):
        pid = int(data.pop('parent_id'))
        verify_parent_id(pid, guild_id=guild_id)
    else:
        pid = 0

    position = int(data.pop('position'))

    verify_channel_position(pos=position, guild_id=guild_id)

    name = str(data['name'])[:30].lower().replace(' ', '-')

    kwargs = {
        'id': snowflake(),
        'guild_id': guild_id,
        'name': name,
        'topic': str(data.get('topic', ''))[:1024],
        'slowmode_timeout': slowmode,
        'type': int(data.get('type', 1)),
        'parent_id': pid,
        'position': position,
    }

    channel: GuildChannel = GuildChannel.create(**kwargs)
    d = to_dict(channel)

    await guild_event('CHANNEL_CREATE', d=d)

    return jsonify(d)


@bp.route('/guilds/<int:guild_id>/channels/<int:channel_id>', methods=['GET'])
async def get_guild_channel(guild_id: int, channel_id: int):
    channel: GuildChannel = list(
        validate_channel(
            token=request.headers.get('Authorization'),
            guild_id=guild_id,
            channel_id=channel_id,
            permission='view_channels',
        )
    )[2]

    return jsonify(to_dict(channel))
