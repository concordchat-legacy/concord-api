# Copyright 2021 Concord, Inc.
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
from blacksheep.server.controllers import Controller, get
from ..utils import jsonify

class Public(Controller):
    @get('/changelog')
    async def get_changelog(self):
        return jsonify({'v': '5', 'msg': 'flags: ignore-version,available,changelog,recommended,newest'})

    @get('/shops/themes')
    async def get_themes(self):
        return jsonify([])

    @get('/shops/templates')
    async def get_guild_templates(self):
        return jsonify([])

    @get('/shops')
    async def get_shops(self):
        return jsonify(['themes', 'templates'])

    @get('/discovery/guilds')
    async def get_dicovery_guilds(self):
        return jsonify([])

    @get('/discovery/bots')
    async def get_discovery_bots(self):
        return jsonify([])
