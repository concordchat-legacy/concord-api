import orjson
from blacksheep import Request
from blacksheep.server.controllers import Controller, get, post

from ..checks import audit, validate_member
from ..database import Audit, to_dict
from ..errors import NotFound
from ..utils import AuthHeader, jsonify


class AuditLogger(Controller):
    @get('/guilds/{int:guild_id}/audits')
    async def get_guild_audits(self, guild_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

        audits_ = Audit.objects(Audit.guild_id == guild_id).all()

        audits = []

        for audit in audits_:
            audits.append(to_dict(audit))

        return jsonify(audits)

    @get('/guilds/{int:guild_id}/audits/{int:audit_id}')
    async def get_guild_audit(self, guild_id: int, audit_id: int, auth: AuthHeader):
        validate_member(token=auth.value, guild_id=guild_id)

        try:
            audit = Audit.objects(
                Audit.guild_id == guild_id, Audit.audit_id == audit_id
            ).get()
        except:
            raise NotFound()

        return jsonify(to_dict(audit))

    @post('/guilds/{int:guild_id}/audits')
    async def create_audit(self, guild_id: int, auth: AuthHeader, request: Request):
        _, me = validate_member(token=auth.value, guild_id=guild_id)

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
