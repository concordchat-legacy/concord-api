# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
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
