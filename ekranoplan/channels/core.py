from blacksheep import Request
from blacksheep.server.controllers import Controller, get, post

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
from ..redis_manager import channel_event
from ..utils import AuthHeader, jsonify


class ChannelCore(Controller):
    @post(
        '/guilds/{int:guild_id}/channels',
    )
    async def create_channel(
        self, guild_id: int, request: Request, auth: AuthHeader
    ):
        member, me = validate_member(auth.value, guild_id)

        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        if guild == None:
            raise NotFound()

        permissions = None

        if member.roles == []:
            permissions = guild.permissions
        else:
            id = member.roles[0]

            role: Role = Role.objects(
                Role.id == id, Role.guild_id == guild_id
            ).get()

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
            if (
                int(data.get('slowmode_timeout')) > 21600
                or data.get('slowmode') < 0
            ):
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

        await channel_event(
            'CREATE',
            to_dict(channel),
            to_dict(channel),
            guild_id=guild_id,
            is_message=False,
        )

        return jsonify(d)

    @get(
        '/guilds/{int:guild_id}/channels/{int:channel_id}',
    )
    async def get_guild_channel(
        self, guild_id: int, channel_id: int, auth: AuthHeader
    ):
        channel: GuildChannel = list(
            validate_channel(
                token=auth.value,
                guild_id=guild_id,
                channel_id=channel_id,
                permission='view_channels',
            )
        )[2]

        return jsonify(to_dict(channel))
