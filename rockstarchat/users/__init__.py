from flask import Blueprint
from .core import get_me, get_user

bp = Blueprint('users', __name__)

bp.add_url_rule('/@me', view_func=get_me, methods=['GET'])
bp.add_url_rule('/<user_id>', view_func=get_user, methods=['GET'])