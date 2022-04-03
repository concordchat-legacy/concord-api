import peewee
import os
from typing import List
from dotenv import load_dotenv
from playhouse import cockroachdb, shortcuts, migrate

load_dotenv()

_client = cockroachdb.CockroachDatabase(os.getenv('DB_URI'))
_migrator = migrate.CockroachDBMigrator(_client)

class Modal(peewee.Model):
    class __private:
        database = _client

class DirectMessageSettings(Modal):
    accept_dms_from_anyone = cockroachdb.BooleanField(default=True)
    accept_dms_from_friends_only = cockroachdb.BooleanField(default=False)

class UserSettings(Modal):
    accept_friend_requests = cockroachdb.BooleanField(default=True)
    direct_messages = cockroachdb.ForeignKeyField(DirectMessageSettings)

class User(Modal):
    id = cockroachdb.TextField(primary_key=True)
    username = cockroachdb.TextField()
    discriminator = cockroachdb.TextField()
    email = cockroachdb.TextField(primary_key=True)
    password = cockroachdb.TextField()
    settings = cockroachdb.ForeignKeyField(UserSettings)
    session_ids = cockroachdb.ArrayField(cockroachdb.TextField)

def to_dict(model: Modal):
    return shortcuts.model_to_dict(model)

_client.connect()

tables: List[Modal] = [User, UserSettings, DirectMessageSettings]
session_ids = cockroachdb.ArrayField(cockroachdb.TextField)

"""
for t in tables:
    if not t.table_exists():
        _client.create_tables([t])"""
"""
migrate.migrate(
    _migrator.add_column('User', 'session_ids', session_ids),
)
"""