# Copyright 2021 Concord, Inc.
# See LICENSE for more information.
from blacksheep.server.controllers import Controller, get, patch, post

from ..checks import validate_member
from ..database import Role, to_dict
from ..errors import NotFound
from ..utils import AuthHeader, jsonify


class Roles(Controller):
    @post('/guilds/{int:guild_id}/roles')
    async def create_role(self, guild_id: int):
        return jsonify('')

    @patch('/guilds/{int:guild_id}/roles/{int:role_id}')
    async def edit_role(self, guild_id: int, role_id: int):
        return jsonify('')

    @get('/guilds/{int:guild_id}/roles/{int:role_id}')
    async def get_role(self, guild_id: int, role_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

        try:
            roles = Role.objects(Role.guild_id == guild_id, Role.id == role_id).get()
        except:
            raise NotFound()

        return jsonify(to_dict(roles))

    @get('/guilds/{int:guild_id}/roles')
    async def get_roles(self, guild_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

        _rs = Role.objects(Role.guild_id == guild_id).all()
        roles = []

        for role in _rs:
            roles.append(to_dict(role))

        return jsonify(roles)
