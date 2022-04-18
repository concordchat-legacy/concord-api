from typing import List
from cassandra.cqlengine import query

from .database import Member, Message, User
from .errors import Forbidden
from .flags import UserFlags, GuildPermissions
from .tokens import verify_token
from .randoms import get_bucket


def valid_session(token: str) -> User:
    return verify_token(token=token)


def validate_user(token: str, stop_bots: bool = False) -> User:
    user = valid_session(token=token)

    if stop_bots:
        if user.bot:
            raise Forbidden()

    return user


def validate_member(token: str, guild_id: int, *, needs_permission: str = None) -> tuple[Member, User]:
    user = validate_user(token=token)
    objs = Member.objects(Member.id == user.id, Member.guild_id == guild_id)

    try:
        member: Member = objs.get()
    except (query.DoesNotExist):
        raise Forbidden()

    if needs_permission:
        if member.owner or needs_permission == 'owner':
            return member, user

    return member, user


def validate_admin(token: str):
    admin = validate_user(token=token)

    flags = UserFlags(admin.flags)

    if not flags.staff:
        raise Forbidden()

    return admin

def search_messages(channel_id: int, message_id: int = None, limit: int = 50):
    current_bucket = get_bucket(channel_id)
    collected_messages = []
    if message_id is None:
        for bucket in range(current_bucket):
            msgs = Message.objects(Message.channel_id == channel_id, Message.bucket_id == bucket).limit(limit).order_by('-id')

            msgs = msgs.all()

            collected_messages.append(msgs)

            if len(collected_messages) > limit:
                collected_messages = collected_messages[limit:]
                break

        return collected_messages
    else:
        for bucket in range(current_bucket):
            pmsg = Message.objects(
                Message.id == message_id,
                Message.channel_id == channel_id,
                Message.bucket_id == bucket
            )

            try:
                msg = pmsg.get()
            except:
                pass
            else:
                return msg
