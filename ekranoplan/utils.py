import orjson
from blacksheep import Content, FromHeader, Response

NONMESSAGEABLE = [0]
MESSAGEABLE = [1]
CHANNEL_TYPES = [0, 1]
VALID_GUILD_FEATURES = [
    'THREAD_CHANNELS',
    'MESSAGE_ATTACHMENTS',
    'EMOJIS',
    'GUILD_ICONS',
    'GUILD_BANNERS',
    'GUILD_MEMBER_BANNERS',
    'GUILD_MEMBER_AVATARS',
    'CHANNEL_THREADS',
    'POLL_CHANNELS',
    'WEBHOOKS',
    'BOTS',
    'AUDIT_LOG',
    'VOICE_CHANNELS',
    'GUILD_DISCOVERY',
    'GUILD_EVENTS',
    'GUILD_SAFETY',
    'ANOUNCEMENT_CHANNELS',
    'ROLE_AVATARS',
    'TEXT_IN_VOICE_CHANNELS',
    'WELCOME_VERIFICATION',
    'FORM_CHANNELS'
]
VALID_THEMES = [
    'DARK',
    'LIGHT'
]
VALID_LOCALES = [
    'en_US',
    'en_UK',
]


class AuthHeader(FromHeader[str]):
    name = 'Authorization'


def jsonify(data: dict, status: int = 200) -> Response:
    return Response(
        status=status,
        headers=None,
        content=Content(b'application/json', orjson.dumps(data)),
    )
