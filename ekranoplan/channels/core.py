import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, delete, get, patch, post

from ..checks import (
    delete_channel,
    validate_channel,
    validate_member,
    verify_channel_position,
    verify_parent_id,
    verify_permission_overwrite,
)
from ..database import Guild, GuildChannel, PermissionOverWrites, Role, to_dict
from ..errors import BadData, Forbidden, NotFound
from ..flags import GuildPermissions
from ..randoms import factory
from ..redis_manager import channel_event
from ..utils import NONMESSAGEABLE, AuthHeader, jsonify


class ChannelCore(Controller):
    @post(
        '/guilds/{int:guild_id}/channels',
    )
    async def create_channel(self, guild_id: int, request: Request, auth: AuthHeader):
        member, _ = validate_member(auth.value, guild_id)

        guild: Guild = Guild.objects(Guild.id == guild_id).get()

        if guild == None:
            raise NotFound()

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
            and not member.owner
            and not calc.administator
        ):
            raise Forbidden()

        data: dict = request.json(orjson.loads)

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

        chek = str(position)
        if chek.startswith('-'):
            raise BadData()

        channels = GuildChannel.objects(GuildChannel.guild_id == guild_id).all()

        await verify_channel_position(position, len(channels), guild_id=guild_id)

        name = (
            str(data['name'])[:45].lower().replace(' ', '-')
            if int(data.get('type')) not in NONMESSAGEABLE
            else str(data['name'])[:45]
        )

        kwargs = {
            'id': factory().formulate(),
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

    @delete('/guilds/{int:guild_id}/channels/{int:channel_id}')
    async def delete_channel(self, guild_id: int, channel_id: int, auth: AuthHeader):
        _, _, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='manage_channels',
        )

        delete_channel(channel=channel)

        await channel_event(
            'DELETE',
            channel=channel,
            data={'channel_id': channel.id, 'guild_id': guild_id},
        )

        return jsonify({}, 203)

    @patch('/guilds/{int:guild_id}/channels/{int:channel_id}')
    async def edit_channel(
        self, guild_id: int, channel_id: int, auth: AuthHeader, request: Request
    ):
        _, _, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='manage_channels',
        )

        data: dict = await request.json(orjson.loads)

        if data.get('name'):
            channel.name = str(data.pop('name'))[:45]

        if data.get('position'):
            await verify_channel_position(
                int(data.pop('position')), channel.position, guild_id=guild_id
            )
            channel.position = int(data.pop('position'))

        if data.get('permission_overwrites'):
            permission_overwrites = list(data.pop('permission_overwrites'))
            overwrites = []
            for overwrite in permission_overwrites:
                overwrites.append(
                    PermissionOverWrites(**verify_permission_overwrite(dict(overwrite)))
                )
            # channel.permission_overwrites = set(overwrites)

        if data.get('topic'):
            channel.topic = str(data.pop('topic'))[:1024]

        if data.get('slowmode_timeout'):
            smto = round(int(data.pop('slowmode_timeout')))

            if smto > 21600 or smto < 0:
                raise BadData()

            channel.slowmode_timeout = smto

        if data.get('parent_id'):
            parent = verify_parent_id(int(data.pop('parent_id')), guild_id=guild_id)

            channel.parent_id = parent.id

        channel = channel.save()

        await channel_event(
            'EDIT',
            to_dict(channel),
            to_dict(channel),
            guild_id=guild_id,
        )

        return jsonify(to_dict(channel))

    @get(
        '/guilds/{int:guild_id}/channels/{int:channel_id}',
    )
    async def get_guild_channel(self, guild_id: int, channel_id: int, auth: AuthHeader):
        channel: GuildChannel = list(
            validate_channel(
                token=auth.value,
                guild_id=guild_id,
                channel_id=channel_id,
                permission='view_channels',
            )
        )[2]

        return jsonify(to_dict(channel))
