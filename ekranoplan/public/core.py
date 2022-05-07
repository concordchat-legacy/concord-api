# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from blacksheep.server.controllers import Controller, get
from ..utils import jsonify

class Public(Controller):
    @get('/changelog')
    async def get_changelog(self):
        return jsonify({'name': '', 'description': '', 'banner_img': '', 'created_at': '', '_traced': '[false]'})

    @get('/discovery/guilds')
    async def get_dicovery_guilds(self):
        return jsonify([])

    @get('/discovery/bots')
    async def get_discovery_bots(self):
        return jsonify([])
