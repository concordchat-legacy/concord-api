import quart.flask_patch
import flask_limiter
import flask_limiter.util
from .randoms import snowflake

limiter = flask_limiter.Limiter(
    headers_enabled=True,
    default_limits=['50/second'],
    retry_after='delta-seconds',
    key_prefix=hex(int(snowflake())),
    key_func=flask_limiter.util.get_remote_address
)
