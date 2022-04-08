from cassandra.cqlengine import query
from .database import User, Member
from .errors import Forbidden, Unauthorized

def valid_session(id: str) -> tuple[bool, User]:
    try:
        filtration: User = User.objects().allow_filtering()
        user = filtration.get(session_ids__contains=id)
    except(query.DoesNotExist):
        return False, None
    else:
        return True, user

def validate_user(session_id: str) -> User:
    is_value, user = valid_session(session_id)

    if not is_value:
        raise Unauthorized()
    else:
        return user

def validate_member(session_id: str, guild_id: int) -> tuple[Member, User]:
    user = validate_user(session_id)
    objs = Member.objects(Member.id == user.id, Member.guild_id == guild_id)
    try:
        member = objs.get()
    except(query.DoesNotExist):
        raise Forbidden()

    return member, user
