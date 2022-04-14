from flask import Blueprint
from .users import _create_user

bp = Blueprint('admin', __name__)

bp.add_url_rule('', methods=['POST', 'PUT'], view_func=_create_user, strict_slashes=False)