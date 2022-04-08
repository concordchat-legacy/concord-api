import flask_limiter
import flask_limiter.util
from .randoms import _id

limiter = flask_limiter.Limiter(
    headers_enabled=True,
    default_limits=['20/second'],
    retry_after='delta-seconds',
    key_prefix=hex(int(_id())),
    key_func=flask_limiter.util.get_remote_address
)
