import datetime
import os
import dotenv
from cassandra.cqlengine import connection, models, columns, usertype, management
from cassandra.auth import PlainTextAuthProvider

dotenv.load_dotenv()

cloud = {
    'secure_connect_bundle': os.getcwd() + '\\rockstarchat\\static\\bundle.zip'
}
auth_provider = PlainTextAuthProvider(os.getenv('client_id'), os.getenv('client_secret'))

connection.setup([], 'rockstar', cloud=cloud, auth_provider=auth_provider, metrics_enabled=True)

def _get_date():
    return datetime.datetime.now(datetime.timezone.utc)

class SettingsType(usertype.UserType):
    accept_friend_requests = columns.Boolean()
    accept_direct_messages = columns.Boolean()

class User(models.Model):
    __table_name__ = 'users'
    id = columns.BigInt(primary_key=True, partition_key=False, clustering_order='ASC')
    username = columns.Text(max_length=40, partition_key=True)
    discriminator = columns.Integer(index=True, partition_key=True)
    email = columns.Text(max_length=100)
    password = columns.Text()
    flags = columns.Integer()
    avatar = columns.Text(default='')
    banner = columns.Text(default='')
    locale = columns.Text(default='EN_US/EU')
    joined_at = columns.DateTime(default=_get_date)
    bio = columns.Text(max_length=4000)
    settings = columns.UserDefinedType(SettingsType)
    session_ids = columns.List(columns.Text)
    verified = columns.Boolean(default=False)
    system = columns.Boolean(default=False)

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
    session_ids = columns.List(columns.Text)
    verified = columns.Boolean()
    system = columns.Boolean()

class Guild(models.Model):
    __table_name__ = 'guilds'
    id = columns.BigInt(primary_key=True, partition_key=True)
    name = columns.Text(partition_key=True, max_length=30)
    description = columns.Text(max_length=4000)
    vanity_url = columns.Text(default=None, index=True)
    icon = columns.Text(default='')
    banner = columns.Text(default='')
    owner_id = columns.BigInt(primary_key=True, partition_key=True)
    nsfw = columns.Boolean(default=False)
    large = columns.Boolean(primary_key=True)
    perferred_locale = columns.Text(default='EN_US/EU')
    permissions = columns.BigInt(default=0)
    splash = columns.Text(default='')

class Member(models.Model):
    __table_name__ = 'members'
    id = columns.BigInt(primary_key=True, partition_key=True)
    guild_id = columns.BigInt(primary_key=True, partition_key=True)
    user = columns.UserDefinedType(UserType)
    avatar = columns.Text(default='')
    banner = columns.Text(default='')
    joined_at = columns.DateTime(default=_get_date)
    roles = columns.List(columns.BigInt)
    nick = columns.Text(default='')

management.sync_table(User)
management.sync_table(Guild)
management.sync_table(Member)
