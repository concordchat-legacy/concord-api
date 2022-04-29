import orjson
from blacksheep import Content, FromHeader, Response

NONMESSAGEABLE = [ 0 ]
MESSAGEABLE = [ 1 ]
CHANNEL_TYPES = [ 0, 1 ]

class AuthHeader(FromHeader[str]):
    name = 'Authorization'


def jsonify(data: dict, status: int = 200) -> Response:
    return Response(
        status=status,
        headers=None,
        content=Content(b'application/json', orjson.dumps(data)),
    )
