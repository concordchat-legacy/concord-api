import flask_limiter
import flask_limiter.util
from .randoms import snowflake

limiter = flask_limiter.Limiter(
    headers_enabled=False,
    default_limits=['20/second'],
    key_prefix=hex(int(snowflake())),
    key_func=flask_limiter.util.get_remote_address
)
