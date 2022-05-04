# Copyright 2021 Redux, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
    'FORM_CHANNELS',
]
VALID_THEMES = ['DARK', 'LIGHT']
VALID_LOCALES = [
    'en_US',
    'en_UK',
]
SCIENCE_TYPES = [
    'app-opened',
    'guild-opened',
    'channel-opened',
    'pane-opened',
    'changelog-viewed',
]


class AuthHeader(FromHeader[str]):
    name = 'Authorization'


def jsonify(data: dict, status: int = 200) -> Response:
    return Response(
        status=status,
        headers=None,
        content=Content(b'application/json', orjson.dumps(data)),
    )
