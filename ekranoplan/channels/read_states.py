from blacksheep.server.controllers import Controller, get, post
from cassandra.cqlengine.query import DoesNotExist

from ..checks import search_messages, validate_channel, validate_user
from ..database import ReadState, to_dict
from ..errors import BadData, NotFound
from ..utils import NONMESSAGEABLE, AuthHeader, jsonify


class ReadStates(Controller):
    @post(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/messages/{int:message_id}/ack',
    )
    async def ack_guild_message(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        auth: AuthHeader,
    ):
        _, user, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='read_message_history',
            stop_bots=True,
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        message = search_messages(channel_id=channel_id, message_id=message_id)

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

    @get(
        '/guilds/{int:guild_id}/channels/{int:channel_id}/readstate',
    )
    async def get_guild_channel_read_state(
        self, guild_id: int, channel_id: int, auth: AuthHeader
    ):
        _, user, channel, _ = validate_channel(
            token=auth.value,
            guild_id=guild_id,
            channel_id=channel_id,
            permission='read_message_history',
            stop_bots=True,
        )

        if channel.type in NONMESSAGEABLE:
            raise BadData()

        try:
            obj = ReadState.objects(
                ReadState.user_id == user.id,
                ReadState.channel_id == channel_id,
            ).get()
        except (DoesNotExist):
            raise NotFound()

        return jsonify(to_dict(obj))

    @get('/readstates')
    async def get_readstates(self, auth: AuthHeader):
        me = validate_user(auth.value, stop_bots=True)

        _readstates = ReadState.objects(ReadState.id == me.id).all()

        readstates = []

        for readstate in _readstates:
            readstates.append(to_dict(readstate))

        return jsonify(readstates)
