from quart import Blueprint
from .core import create_guild

bp = Blueprint('guilds', __name__)

bp.add_url_rule('', view_func=create_guild, strict_slashes=False, methods=['POST'])
