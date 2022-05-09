# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from copy import copy

import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, delete, get, patch, post

from ..checks import audit, search_messages, validate_channel, verify_slowmode
from ..database import ChannelSlowMode, GuildChannelPin, Message, _get_date, to_dict
from ..errors import BadData, Forbidden
from ..events import channel_event
from ..randoms import factory, get_bucket
from ..utils import NONMESSAGEABLE, AuthHeader, jsonify


class Messages(Controller):
    @get(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/messages/{int:message_id}',
    )
    async def get_guild_channel_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        auth: AuthHeader,
    ):
        _, _, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='read_message_history',
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        msg = search_messages(channel_id=channel.id, message_id=message_id)

        if msg.author_id is None:
            msg.delete()
            return jsonify('', 404)

        return jsonify(to_dict(msg))

    @get(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/messages',
    )
    async def get_guild_channel_messages(
        self,
        guild_id: int,
        channel_id: int,
        auth: AuthHeader,
        request: Request,
    ):
        _, _, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='read_message_history',
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        limit = int(request.query.get('limit', '50'))

        if limit > 10000:
            raise BadData()

        _msgs = search_messages(channel_id=channel.id, limit=limit)
        msgs = []

        for msgobj in _msgs:
            for msg in msgobj:
                msgs.append(to_dict(msg))

        return jsonify(msgs)

    @post(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/messages',
    )
    async def create_guild_channel_message(
        self,
        guild_id: int,
        channel_id: int,
        request: Request,
        auth: AuthHeader,
    ):
        # TODO: Attachments/Image Embeds
        member, me, channel, perms = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='send_messages',
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        verify_slowmode(member.id, channel.id)

        d: dict = await request.json(orjson.loads)

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
            referenced_message = referenced_message.message_id
        else:
            referenced_message = None

        data = {
            'message_id': factory().formulate(),
            'channel_id': channel_id,
            'bucket_id': get_bucket(channel_id),
            'guild_id': guild_id,
            'author_id': me.id,
            'content': str(d['content'])[:5000],
            'mentions_everyone': mentions_everyone,
            'referenced_message_id': referenced_message or 0,
        }

        msg: Message = Message.create(**data)

        pm = f'# User `{str(me.username)}`/`{str(me.id)}` Created Message `{str(msg.message_id)}` On `{str(msg.created_at)}` In `{str(channel.id)}`:\n'

        if msg.referenced_message_id != 0:
            pm += f'- This Message Referenced `{str(msg.referenced_message_id)}`\n'

        pm += f' On Bucket `{str(msg.bucket_id)}`'
        if msg.mentions_everyone:
            pm += '- This Message Mentioned `@everyone`\n'

        pm += f'- Message Content is `{str(len(msg.content))}` lines long'

        audit(
            'MESSAGE_CREATE',
            guild_id=guild_id,
            postmortem=pm,
            audited=me.id,
            object_id=msg.message_id,
        )

        await channel_event(
            'CREATE',
            to_dict(channel),
            to_dict(msg),
            guild_id=guild_id,
            is_message=True,
        )

        if channel.slowmode_timeout != 0:
            slowmode: ChannelSlowMode = ChannelSlowMode.create(
                id=member.id, channel_id=channel_id
            )
            slowmode.ttl(channel.slowmode_timeout)

        return jsonify(to_dict(msg))

    @patch(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/messages/{int:message_id}',
    )
    async def edit_guild_channel_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        auth: AuthHeader,
        request: Request,
    ):
        member, me, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission=None,
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        msg = search_messages(channel_id=channel.id, message_id=message_id)

        if msg is None:
            raise BadData()

        if msg.author_id != member.id:
            raise Forbidden()

        d: dict = await request.json(orjson.loads)

        if d.get('content'):
            msg.content = str(d.pop('content'))[:5000]

        msg.last_edited = _get_date()
        old_msg = copy(msg)

        msg = msg.save()

        pm = f'# User `{me.username}/{str(member.id)}` Edited Message `{str(msg.id)}` On `{str(msg.last_edited)}`\n\n'
        pm += f'- New Content is `{msg.content}`\n'
        pm += f'- Old Content is `{old_msg.content}`'

        await channel_event(
            'EDIT',
            to_dict(channel),
            to_dict(msg),
            guild_id=guild_id,
            is_message=True,
        )

        audit(
            'MESSAGE_EDIT',
            guild_id=guild_id,
            postmortem=pm,
            audited=member.id,
            object_id=message_id,
        )

        return jsonify(to_dict(msg))

    @delete(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/messages/{int:message_id}',
    )
    async def delete_guild_channel_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        auth: AuthHeader,
    ):
        _, me, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='manage_messages',
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        msg = search_messages(channel_id=channel.id, message_id=message_id)

        if msg is None:
            raise BadData()

        if msg.pinned:
            pin: GuildChannelPin = GuildChannelPin.objects(
                GuildChannelPin.channel_id == channel_id,
                GuildChannelPin.message_id == message_id,
            ).get()
            pin.delete()
            await channel_event(
                'UNPIN',
                to_dict(channel),
                {
                    'guild_id': guild_id,
                    'channel_id': channel_id,
                    'message_id': message_id,
                },
                guild_id=guild_id,
                is_message=True,
            )

        msg.delete()

        r = jsonify('')
        r.status_code = 204

        await channel_event(
            'DELETE',
            to_dict(channel),
            {
                'id': message_id,
                'channel_id': channel_id,
                'guild_id': guild_id,
            },
            guild_id=guild_id,
            is_message=True,
        )
        pm = f'# User `{me.username}/{str(me.id)}` Deleted Message `{msg.message_id}` On `{str(_get_date())}`\n\n'
        pm += f'- Message Author was `{str(msg.author_id)}`\n'
        pm += f'- Message Content was `{msg.content}`\n'
        pm += f'- Message Channel was `{str(msg.channel_id)}`'

        audit(
            'MESSAGE_DELETE',
            guild_id=guild_id,
            postmortem=pm,
            audited=me.id,
            object_id=msg.id,
        )

        return r

    @post(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/pins/{int:message_id}',
    )
    async def pin_guild_channel_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        auth: AuthHeader,
    ):
        _, me, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='manage_channel_pins',
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        msg = search_messages(channel_id=channel.id, message_id=message_id)

        if msg is None:
            raise BadData()

        msg.pinned = True

        possibly_not_empty = GuildChannelPin.objects(
            GuildChannelPin.channel_id == channel_id,
            GuildChannelPin.message_id == message_id,
        )

        if possibly_not_empty.all() != []:
            raise BadData()

        pin: GuildChannelPin = GuildChannelPin.create(
            channel_id=channel_id, message_id=message_id
        )
        msg = msg.save()

        ret = {
            'pinned_data': to_dict(pin),
            'message_pinned': to_dict(msg),
        }

        pm = f'# User `{me.username}`/`{str(me.id)}` Pinned Message `{str(pin.message_id)}` On `{str(_get_date())}`\n\n'
        pm += f'- Channel ID `{str(channel.id)}`\n'

        await channel_event(
            'PIN',
            to_dict(channel),
            ret,
            guild_id=guild_id,
            is_message=True,
        )

        audit(
            'PIN_CREATE',
            guild_id=guild_id,
            postmortem=pm,
            audited=me.id,
            object_id=channel_id,
        )

        return jsonify(ret)

    @delete(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/pins/{int:message_id}',
    )
    async def unpin_guild_channel_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        auth: AuthHeader,
    ):
        _, me, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='manage_channel_pins',
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        msg = search_messages(channel_id=channel.id, message_id=message_id)

        if msg is None or not msg.pinned:
            raise BadData()

        msg.pinned = False
        pin: GuildChannelPin = GuildChannelPin.objects(
            GuildChannelPin.channel_id == channel_id,
            GuildChannelPin.message_id == message_id,
        ).get()
        pin.delete()
        msg.save()

        r = jsonify('', 204)

        await channel_event(
            'UNPIN',
            to_dict(channel),
            {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'message_id': message_id,
            },
            guild_id=guild_id,
            is_message=True,
        )

        pm = f'# User `{str(me.id)}`/`{me.username}` Unpinned Message `{str(msg.id)}` On `{str(_get_date())}`\n\n'
        pm += f'- Channel ID `{str(channel.id)}`'

        audit(
            'PIN_REMOVE',
            guild_id=guild_id,
            postmortem=pm,
            audited=me.id,
            object_id=channel.id,
        )

        return r
