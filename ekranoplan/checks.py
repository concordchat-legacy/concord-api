from typing import List, Union

from cassandra.cqlengine import query

from .database import (
    ChannelSlowMode,
    Guild,
    GuildChannel,
    Member,
    Message,
    PermissionOverWrites,
    Role,
    User,
    to_dict,
)
from .errors import BadData, Conflict, Forbidden, NotFound
from .flags import GuildPermissions, UserFlags
from .randoms import get_bucket
from .redis_manager import channel_event
from .tokens import verify_token


def validate_user(token: str, stop_bots: bool = False) -> User:
    user = verify_token(token=token)

    if stop_bots:
        if user.bot:
            raise Forbidden()

    return user


def validate_member(
    token: str, guild_id: int, *, stop_bots: bool = False
) -> tuple[Member, User]:
    user = validate_user(token=token, stop_bots=stop_bots)
    objs = Member.objects(Member.id == user.id, Member.guild_id == guild_id)

    try:
        member: Member = objs.get()
    except (query.DoesNotExist):
        raise Forbidden()

    return member, user


def validate_admin(token: str):
    admin = validate_user(token=token)

    flags = UserFlags(admin.flags)

    if not flags.staff:
        raise Forbidden()

    return admin


def get_member_permissions(
    member: Member,
):
    if list(member.roles) == []:
        guild: Guild = Guild.objects(Guild.id == member.guild_id).get()
        permissions = GuildPermissions(guild.permissions)
    else:
        role_id: int = list(member.roles)[0]

        role: Role = Role.objects(role_id).get()

        permissions = GuildPermissions(role.permissions)

    return permissions


def validate_channel(
    token: str,
    guild_id: int,
    channel_id: int,
    permission: Union[str, List[str]],
    *,
    stop_bots: bool = False,
) -> tuple[Member, User, GuildChannel, Union[GuildPermissions, None]]:
    member, user = validate_member(token=token, guild_id=guild_id, stop_bots=stop_bots)

    try:
        channel: GuildChannel = GuildChannel.objects(
            id=channel_id, guild_id=guild_id
        ).get()
    except (query.DoesNotExist):
        raise NotFound()

    if permission is None:

        if member.owner:
            return member, user, channel, None

        user_found = False
        for overwrite in channel.permission_overwrites:
            assert isinstance(overwrite, PermissionOverWrites)

            if overwrite.id == user.id:
                user_found = True
                allow_permissions = GuildPermissions(overwrite.allow)
                disallow_permissions = GuildPermissions(overwrite.deny)
                break

        if not user_found:
            if list(member.roles) == []:
                guild: Guild = Guild.objects(Guild.id == guild_id).get()
                permissions = GuildPermissions(guild.permissions)
            else:
                role_id: int = list(member.roles)[0]

                role: Role = Role.objects(role_id).get()

                permissions = GuildPermissions(role.permissions)

            if permissions.administator:
                return member, user, channel, permissions

            if isinstance(permission, list):
                for perm in permission:
                    if not getattr(permissions, perm):
                        raise Forbidden()
            else:
                if not getattr(permissions, perm):
                    raise Forbidden()

            return member, user, channel, permissions
        else:
            if isinstance(permission, list):
                for perm in permission:
                    if getattr(disallow_permissions, perm):
                        raise Forbidden()

                    if not getattr(allow_permissions, perm):
                        raise Forbidden()
            else:
                if getattr(disallow_permissions, permission):
                    raise Forbidden()

                if not getattr(allow_permissions, permission):
                    raise Forbidden()

            return member, user, channel, permissions

    else:
        return member, user, channel, None


def search_messages(
    channel_id: int, message_id: int = None, limit: int = 50
) -> Union[List[Message], Message, None]:
    current_bucket = get_bucket(channel_id)
    collected_messages = []
    if message_id is None:
        for bucket in range(current_bucket + 1):
            msgs = (
                Message.objects(
                    Message.channel_id == channel_id,
                    Message.bucket_id == bucket,
                )
                .limit(limit)
                .order_by('-id')
            )

            msgs = msgs.all()

            collected_messages.append(msgs)

            if len(collected_messages) > limit:
                collected_messages = collected_messages[limit:]
                break

        return collected_messages
    else:
        for bucket in range(current_bucket + 1):
            pmsg = Message.objects(
                Message.id == message_id,
                Message.channel_id == channel_id,
                Message.bucket_id == bucket,
            )

            try:
                msg = pmsg.get()
            except:
                pass
            else:
                return msg


def verify_parent_id(parent: int, guild_id: int) -> GuildChannel:
    channel: GuildChannel = GuildChannel.objects(
        GuildChannel.id == parent, GuildChannel.guild_id == guild_id
    )

    try:
        channel: GuildChannel = channel.get()
    except (query.DoesNotExist):
        raise BadData()

    return channel


async def verify_channel_position(pos: int, current_pos: int, guild_id: int, gathered_channels: List[GuildChannel] = None):
    if gathered_channels:
        guild_channels = gathered_channels
    else:
        guild_channels: List[GuildChannel] = GuildChannel.objects(
            GuildChannel.guild_id == guild_id
        ).all()

    if len(guild_channels) + 1 < pos:
        raise BadData()

    guild_channels_ = []

    for channel in guild_channels:
        guild_channels_.insert(channel.position, channel)

    guild_channels = guild_channels_

    left_shift = pos > current_pos

    shift_block = (
        guild_channels[current_pos:pos]
        if left_shift
        else guild_channels[pos:current_pos]
    )

    shift = -1 if left_shift else 1

    for channel in shift_block:
        channel.position = channel.position + shift
        channel.save()
        await channel_event(
            'UPDATE', to_dict(channel), to_dict(channel), guild_id=guild_id
        )


def get_cat_channels(category: GuildChannel, _add_one: bool = False):
    channels: List[GuildChannel] = GuildChannel.objects(
        GuildChannel.guild_id == category.guild_id,
        GuildChannel.parent_id == category.id,
    )

    ret = []

    for channel in channels:
        ret.insert(channel.position, channel)

    if _add_one:
        ret.append(None)

    return ret


def verify_permission_overwrite(d: dict):
    data = {
        'id': d['id'],
        'allow': str(d['allow']) if d['allow'] is not None else '0',
        'deny': str(d['deny']) if d['deny'] is not None else '0',
    }

    return data


def verify_slowmode(user_id: int, channel_id: int):
    try:
        ChannelSlowMode.objects(
            ChannelSlowMode.id == user_id, ChannelSlowMode.channel_id == channel_id
        ).get()
    except (query.DoesNotExist):
        ...
    else:
        raise Conflict()


def delete_channel(channel: GuildChannel):
    if channel.type in [1]:
        highest_bucket = get_bucket(channel.id)

        for bucket in range(highest_bucket + 1):
            msgs: List[Message] = Message.objects(
                Message.channel_id == channel.id, Message.bucket_id == bucket
            ).all()

            for msg in msgs:
                msg.delete()
    channel.delete()


def delete_all_channels(guild_id: int):
    channels: List[GuildChannel] = GuildChannel.objects(
        GuildChannel.guild_id == guild_id
    ).all()

    for channel in channels:
        delete_channel(channel)


def modify_member_roles(guild_id: int, member: Member, changed_roles: list):
    roles: List[Role] = Role.objects(
        Role.guild_id == guild_id
    ).all()

    rroles = [r.id for r in roles]
    croles: List[Role] = []

    for role in changed_roles:
        if role not in rroles:
            raise BadData()

        for role_ in roles:
            if role_.id == role:
                croles.append(role_)

    mroles = []

    for _role in member.roles:
        for role in roles:
            if role.id == _role:
                mroles.append(role)

    for role in mroles:
        for role_ in croles:
            if role_.position > role.position:
                raise Forbidden()

    return set(changed_roles)
