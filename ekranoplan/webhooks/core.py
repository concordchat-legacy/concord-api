from blacksheep.server.controllers import Controller, get, post

from ..errors import Forbidden
from ..utils import AuthHeader
from ..checks import validate_member, get_member_permissions
from ..database import Webhook
from ..randoms import factory

class Webhooks(Controller):

    # @post('/guilds/{int:guild_id}/channels/{int:channel_id}/webhooks')
    async def create_webhook(self, guild_id: int, auth: AuthHeader):
        member, _ = validate_member(
            token=auth.value,
            guild_id=guild_id,
        )

        perms = get_member_permissions(member=member)

        if not perms.manage_webhooks and not perms.administator and not member.owner:
            raise Forbidden()

        Webhook.create(

        )
