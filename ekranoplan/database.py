import datetime
import os
from typing import Any

import dotenv
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection, management, models, usertype

dotenv.load_dotenv()

cloud = {'secure_connect_bundle': os.getcwd() + '\\ekranoplan\\static\\bundle.zip'}
auth_provider = PlainTextAuthProvider(
    os.getenv('client_id'), os.getenv('client_secret')
)


def connect():
    try:
        if os.getenv('safe', 'false') == 'true':
            connection.setup(
                [], 'concord', cloud=cloud, auth_provider=auth_provider, connect_timeout=100
            )
        else:
            connection.setup(
                [], 'concord', auth_provider=auth_provider, connect_timeout=100
            )
    except:
        # Just try again
        connect()


default_options = {
    # NOTE: Only let tombstones live for a day
    'gc_grace_seconds': 86400,
}

default_permissions = (
    1 << 0
    | 1 << 6
    | 1 << 10
    | 1 << 11
    | 1 << 12
    | 1 << 14
    | 1 << 15
    | 1 << 16
    | 1 << 18
    | 1 << 25
)

# this makes giving the current date just easier, as cassandra-driver accepts non-async functions
def _get_date():
    return datetime.datetime.now(datetime.timezone.utc)


# NOTE: Users
class SettingsType(usertype.UserType):
    accept_friend_requests = columns.Boolean()
    accept_direct_messages = columns.Boolean()


class User(models.Model):
    __table_name__ = 'users'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=False)
    username = columns.Text(max_length=40)
    discriminator = columns.Integer(index=True)
    email = columns.Text(max_length=100)
    password = columns.Text()
    flags = columns.Integer()
    avatar = columns.Text(default='')
    banner = columns.Text(default='')
    locale = columns.Text(default='EN_US')
    joined_at = columns.DateTime(default=_get_date)
    bio = columns.Text(max_length=4000)
    settings = columns.UserDefinedType(SettingsType)
    verified = columns.Boolean(default=False)
    system = columns.Boolean(default=False)
    early_supporter_benefiter = columns.Boolean(default=True)
    bot = columns.Boolean(default=False)


class UserType(usertype.UserType):
    id = columns.BigInt()
    username = columns.Text()
    discriminator = columns.Integer()
    email = columns.Text()
    password = columns.Text()
    flags = columns.Integer()
    avatar = columns.Text()
    banner = columns.Text()
    locale = columns.Text()
    joined_at = columns.DateTime()
    bio = columns.Text()
    settings = columns.UserDefinedType(SettingsType)
    verified = columns.Boolean()
    system = columns.Boolean()
    early_supporter_benefiter = columns.Boolean()
    bot = columns.Boolean(default=False)


# NOTE: Guilds
class Role(usertype.UserType):
    id = columns.BigInt()
    name = columns.Text(max_length=100)
    color = columns.Integer()
    hoist = columns.Boolean()
    icon = columns.Text()
    position = columns.Integer()
    permissions = columns.BigInt()
    mentionable = columns.Boolean()


class Guild(models.Model):
    __table_name__ = 'guilds'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    name = columns.Text(max_length=40)
    description = columns.Text(max_length=4000)
    vanity_url = columns.Text(default='')
    icon = columns.Text(default='')
    banner = columns.Text(default='')
    owner_id = columns.BigInt(primary_key=True)
    nsfw = columns.Boolean(default=False)
    large = columns.Boolean(primary_key=True, default=False)
    perferred_locale = columns.Text(default='EN_US/EU')
    permissions = columns.BigInt(default=default_permissions)
    splash = columns.Text(default='')
    roles = columns.Set(columns.UserDefinedType(Role))
    features = columns.Set(columns.Text)


class GuildInvite(models.Model):
    __table_name__ = 'guild_invites'
    __options__ = default_options
    id = columns.Text(primary_key=True, partition_key=False)
    guild_id = columns.BigInt(primary_key=True)
    creator_id = columns.BigInt(primary_key=True)
    created_at = columns.DateTime(default=_get_date)


class Member(models.Model):
    __table_name__ = 'members'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True)
    user = columns.UserDefinedType(UserType)
    avatar = columns.Text(default='')
    banner = columns.Text(default='')
    joined_at = columns.DateTime(default=_get_date)
    roles = columns.List(columns.BigInt)
    nick = columns.Text(default='')


## NOTE: Channels/Messages, etc


class PermissionOverWrites(usertype.UserType):
    id = columns.BigInt()
    type = columns.Integer(default=0)
    allow = columns.BigInt()
    deny = columns.BigInt()


class Channel(models.Model):
    __table_name__ = 'channels'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True)
    type = columns.Integer(default=0)
    position = columns.Integer()
    permission_overwrites = columns.UserDefinedType(PermissionOverWrites)
    name = columns.Text(max_length=30)
    topic = columns.Text(max_length=1024)
    slowmode_timeout = columns.Integer()
    recipients = columns.List(columns.UserDefinedType(UserType))
    owner_id = columns.BigInt()
    parent_id = columns.BigInt()
    # NOTE: Store empty buckets to make sure we never go over them
    # NOTE: Maybe store this somewhere else? this could impact read perf
    empty_buckets = columns.Set(columns.Integer)


class EmbedField(usertype.UserType):
    name = columns.Text(max_length=100)
    value = columns.Text()
    inline = columns.Boolean(default=False)


class EmbedAuthor(usertype.UserType):
    name = columns.Text(max_length=100)
    url = columns.Text(max_length=20)
    icon_url = columns.Text(max_length=100)


class EmbedVideo(usertype.UserType):
    url = columns.Text(max_length=30)


class EmbedImage(usertype.UserType):
    url = columns.Text(max_length=30)


class EmbedFooter(usertype.UserType):
    text = columns.Text(max_length=500)
    icon_url = columns.Text(max_length=100)


class Embed(usertype.UserType):
    title = columns.Text(default='', max_length=100)
    description = columns.Text(max_length=4000, default='')
    url = columns.Text(default='')
    timestamp = columns.DateTime()
    color = columns.Integer()
    footer = columns.UserDefinedType(EmbedFooter)
    image = columns.UserDefinedType(EmbedImage)
    video = columns.UserDefinedType(EmbedVideo)
    author = columns.UserDefinedType(EmbedAuthor)
    fields = columns.List(columns.UserDefinedType(EmbedField))


class Reaction(usertype.UserType):
    count = columns.Integer()
    # TODO: Implement Emojis
    emoji = columns.Text()


class Message(models.Model):
    __table_name__ = 'messages'
    __options__ = default_options
    id = columns.BigInt(primary_key=True, partition_key=False, clustering_order='DESC')
    channel_id = columns.BigInt(primary_key=True, partition_key=True)
    bucket_id = columns.Integer(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True)
    author = columns.UserDefinedType(UserType)
    content = columns.Text(max_length=3000)
    created_at = columns.DateTime(default=_get_date)
    last_edited = columns.DateTime()
    tts = columns.Boolean(default=False)
    mentions_everyone = columns.Boolean(default=False)
    mentions = columns.List(columns.UserDefinedType(UserType))
    embeds = columns.List(columns.UserDefinedType(Embed))
    reactions = columns.List(columns.UserDefinedType(Reaction))
    pinned = columns.Boolean(default=False)
    referenced_message_id = columns.BigInt()


class ReadState(models.Model):
    __table_name__ = 'readstates'
    channel_id = columns.BigInt(primary_key=True, partition_key=True)
    user_id = columns.BigInt(primary_key=True, partition_key=True)
    last_message_id = columns.BigInt()


def to_dict(model: models.Model) -> dict:
    initial: dict[str, Any] = model.items()
    ret = dict(initial)

    for name, value in initial:
        if isinstance(value, (usertype.UserType, models.Model)):
            # things like member objects or embeds can have usertypes 3/4 times deep
            # there shouldnt be a recursion problem though
            value = dict(value.items())
            for k, v in value.items():
                if isinstance(v, usertype.UserType):
                    value[k] = to_dict(v)
            ret[name] = value

        # some values are lists of usertypes
        elif isinstance(value, (list, set)):
            if isinstance(value, set):
                value = list(value)

            set_values = []

            for v in value:
                if isinstance(v, usertype.UserType):
                    set_values.append(to_dict(v.items()))
                else:
                    set_values.append(v)

            ret[name] = set_values

        if name == 'id' or name.endswith('_id') and len(str(value)) > 14:
            ret[name] = str(value)
        if name == 'permissions':
            ret[name] = str(value)

    return ret


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    connect()

    # migrate old data

    # NOTE: Types
    management.sync_type('concord', SettingsType)
    management.sync_type('concord', UserType)
    management.sync_type('concord', PermissionOverWrites)
    management.sync_type('concord', EmbedAuthor)
    management.sync_type('concord', EmbedField)
    management.sync_type('concord', EmbedFooter)
    management.sync_type('concord', EmbedImage)
    management.sync_type('concord', EmbedVideo)
    management.sync_type('concord', Embed)
    management.sync_type('concord', Reaction)

    # NOTE: Tables
    management.sync_table(User)
    management.sync_table(Guild)
    management.sync_table(GuildInvite)
    management.sync_table(Member)
    management.sync_table(Channel)
    management.sync_table(Message)
    management.sync_table(ReadState)