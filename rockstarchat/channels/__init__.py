from flask import Blueprint
from .core import create_channel

bp = Blueprint('channels', __name__)
bp.add_url_rule('/guilds/<guild_id>/channels', view_func=create_channel, strict_slashes=False, methods=['POST'])
