# Copyright 2021 Drogon, Inc.
# See LICENSE for more information.
from blacksheep import Request
from blacksheep.server.controllers import Controller, post, put

from ..utils import AuthHeader, jsonify


class AdminUsers(Controller):
    @post('/admin/users')
    @put('/admin/users')
    async def _create_user(self):
        return jsonify('', 201)
