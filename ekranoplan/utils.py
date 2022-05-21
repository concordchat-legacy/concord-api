# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
import os
import re

import orjson
import dotenv
from imgproxy import ImgProxy
from blacksheep import Content, FromHeader, Response

dotenv.load_dotenv()

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
    'FORM_CHANNELS',
]
VALID_THEMES = ['dark', 'light']
VALID_LOCALES = [
    'en-US',
    'en-GB',
]
DEPRECATED_LOCALES = ['en_US', 'en_UK', 'EN_US']
SCIENCE_TYPES = [
    'app-opened',
    'guild-opened',
    'channel-opened',
    'pane-opened',
    'changelog-viewed',
]

IMGPROXY_KEY = os.getenv('IMGPROXY_KEY')
IMGPROXY_SALT = os.getenv('IMGPROXY_SALT')
IMGPROXY_URL = os.getenv('IMGPROXY_URL', 'https://images-ext.concord.chat')

class AuthHeader(FromHeader[str]):
    name = 'Authorization'


def jsonify(data: dict, status: int = 200) -> Response:
    return Response(
        status=status,
        headers=None,
        content=Content(b'application/json', orjson.dumps(data)),
    )


def run_migrations(model):
    if type(model).__name__ == 'Guild':
        if model.perferred_locale in DEPRECATED_LOCALES:
            if 'US' in model.perferred_locale:
                model.perferred_locale = 'en-US'
            else:
                model.perferred_locale = 'en-GB'

            model.save()

    return model

NAME_FILTER = re.compile(r"^[^\u200BА-Яа-яΑ-Ωα-ω]+$")

def proxy_img(url: str, w: int = 0, h: int = 0):
    proxifier = ImgProxy(url, IMGPROXY_URL, key=IMGPROXY_KEY, salt=IMGPROXY_SALT, width=w, height=h)

    return proxifier()
