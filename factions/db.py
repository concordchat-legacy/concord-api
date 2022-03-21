import motor.core as motor
import motor.motor_asyncio as motor_
import asyncio
import os
import dotenv

dotenv.load_dotenv()

loop = asyncio.new_event_loop()
client: motor.AgnosticClient = motor_.AsyncIOMotorClient(
    os.getenv('mongo_uri'), io_loop=loop
)

_factions: motor.AgnosticDatabase = client.get_database('factions')
_users: motor.AgnosticDatabase = client.get_database('users')

users: motor.AgnosticCollection = _users.get_collection('core')
factions: motor.AgnosticCollection = _factions.get_collection('core')

members: motor.AgnosticCollection = _factions.get_collection('members')
invites: motor.AgnosticCollection = _factions.get_collection('invites')

async def index():
    await members.create_index('id')
    await members.create_index('name')

    await factions.create_index('verified')
    await invites.create_index('creator_id')
    await invites.create_index('faction_id')
