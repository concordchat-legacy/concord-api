import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, patch

from ..checks import get_member_permissions, modify_member_roles, validate_member
from ..database import Member, to_dict
from ..errors import Forbidden
from ..utils import AuthHeader, jsonify


class MemberController(Controller):

    # @get('/guilds/{int:guild_id}/members/{int:member_id}')
    async def get_member(self, guild_id: int, member_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

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

        member.save()

        return jsonify(to_dict(member))
