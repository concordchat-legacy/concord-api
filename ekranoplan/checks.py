from cassandra.cqlengine import query

from .database import Member, User
from .errors import Forbidden
from .flags import UserFlags
from .tokens import verify_token


def valid_session(token: str) -> tuple[bool, User]:
    return verify_token(token=token)


def validate_user(token: str, stop_bots: bool = False) -> User:
    user = valid_session(token=token)

    return user


def validate_member(token: str, guild_id: int) -> tuple[Member, User]:
    user = validate_user(token=token)
    objs = Member.objects(Member.id == user.id, Member.guild_id == guild_id)

    try:
        member = objs.get()
    except (query.DoesNotExist):
        raise Forbidden()

    return member, user


def validate_admin(token: str):
    admin = validate_user(token=token)

    flags = UserFlags(admin.flags)

    if not flags.staff:
        raise Forbidden()

    return admin
