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
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch

from ..checks import get_member_permissions, modify_member_roles, validate_member
from ..database import Member, to_dict
from ..errors import Forbidden, NotFound
from ..redis_manager import member_event
from ..utils import AuthHeader, jsonify


class MemberController(Controller):
    @get('/guilds/{int:guild_id}/members/{int:member_id}')
    async def get_member(self, guild_id: int, member_id: int, auth: AuthHeader):
        _, _ = validate_member(token=auth.value, guild_id=guild_id)

        try:
            ret = Member.objects(
                Member.id == member_id, Member.guild_id == guild_id
            ).get()
        except:
            raise NotFound()

        return jsonify(to_dict(ret))

    @get('/guilds/{int:guild_id}/members')
    async def get_members(self, guild_id: int, auth: AuthHeader):
        _, _ = validate_member(token=auth.value, guild_id=guild_id)

        members = Member.objects(Member.guild_id == guild_id).allow_filtering().all()
        ret = []

        for member in members:
            ret.append(to_dict(member))

        return jsonify(ret)

    # consistency
    @patch('/guilds/{int:guild_id}/members/@me')
    @patch('/guilds/{int:guild_id}/members/@me/nick')
    async def edit_me(self, guild_id: int, auth: AuthHeader, request: Request):
        member, _ = validate_member(
            token=auth.value,
            guild_id=guild_id,
        )

        perms = get_member_permissions(member=member)

        if not perms.change_nick and not member.owner and not perms.administator:
            raise Forbidden()

        data: dict = await request.json(orjson.loads)

        nick = str(data['nick'])[:40]

        member.nick = nick

        member = member.save()

        await member_event('UPDATE', member.id, guild_id=guild_id, data=to_dict(member))

        return jsonify(to_dict(member))

    @patch('/guilds/{int:guild_id}/members/{int:member_id}/nick')
    async def edit_member_nick(
        self, guild_id: int, member_id: int, auth: AuthHeader, request: Request
    ):
        member, _ = validate_member(
            token=auth.value,
            guild_id=guild_id,
        )

        perms = get_member_permissions(member=member)

        member: Member = Member.objects(
            Member.id == member_id, Member.guild_id == guild_id
        ).get()

        data = await request.json(orjson.loads)

        if 'nick' in data:
            if not perms.manage_nicks and not member.owner and not perms.administator:
                raise Forbidden()

            member.nick = str(data.pop('nick'))[:40]

        if 'roles' in data:
            if not perms.manage_roles and not member.owner and not perms.administator:
                raise Forbidden()

            member.roles = modify_member_roles(
                guild_id=guild_id, member=member, changed_roles=list(data.pop('roles'))
            )

        member = member.save()

        await member_event('UPDATE', member.id, guild_id=guild_id, data=to_dict(member))

        return jsonify(to_dict(member))
