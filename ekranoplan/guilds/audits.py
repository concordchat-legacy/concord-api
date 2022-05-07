# Copyright 2021 Drogon, Inc.
# See LICENSE for more information.
import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, post

from ..checks import audit, get_member_permissions, validate_member
from ..database import Audit, to_dict
from ..errors import Forbidden, NotFound
from ..utils import AuthHeader, jsonify


class AuditLogger(Controller):
    @get('/guilds/{int:guild_id}/audits')
    async def get_guild_audits(self, guild_id: int, auth: AuthHeader):
        member, _ = validate_member(token=auth.value, guild_id=guild_id)
        perms = get_member_permissions(member)

        if not perms.view_audit_log and not member.owner:
            raise Forbidden()

        audits_ = Audit.objects(Audit.guild_id == guild_id).all()

        audits = []

        for audit in audits_:
            audits.append(to_dict(audit))

        return jsonify(audits)

    @get('/guilds/{int:guild_id}/audits/{int:audit_id}')
    async def get_guild_audit(self, guild_id: int, audit_id: int, auth: AuthHeader):
        member, _ = validate_member(token=auth.value, guild_id=guild_id)
        perms = get_member_permissions(member)

        if not perms.view_audit_log and not member.owner:
            raise Forbidden()

        try:
            audit = Audit.objects(
                Audit.guild_id == guild_id, Audit.audit_id == audit_id
            ).get()
        except:
            raise NotFound()

        return jsonify(to_dict(audit))

    @post('/guilds/{int:guild_id}/audits')
    async def create_audit(self, guild_id: int, auth: AuthHeader, request: Request):
        me, _ = validate_member(token=auth.value, guild_id=guild_id)
        perms = get_member_permissions(me)

        if not perms.create_audits and not me.owner:
            raise Forbidden()

        data = await request.json(orjson.loads)

        ret = audit(
            str(data['type']),
            guild_id=guild_id,
            postmortem=str(data['postmortem']),
            audited=int(data.get('audited') or 0),
            object_id=int(data.get('object_id') or 0),
            user_id=me.id,
        )

        return jsonify(to_dict(ret), 201)
