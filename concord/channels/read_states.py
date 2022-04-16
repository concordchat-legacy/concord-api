from cassandra.cqlengine.query import DoesNotExist
from quart import Blueprint, jsonify, request
from ..checks import validate_user
from ..database import ReadState, Message, Channel, to_dict
from ..errors import BadData

bp = Blueprint('readstates', __name__)

@bp.route('/channels/<int:channel_id>/messages/<int:message_id>/ack', methods=['POST'])
async def ack_message(channel_id: int, message_id: int):
    user_id = validate_user(request.headers.get('Authorization')).id

    try:
        Channel.objects(Channel.id == channel_id).get()
    except(DoesNotExist):
        raise BadData()

    try:
        message: Message = Message.objects(Message.id == message_id, Message.channel_id == channel_id).allow_filtering().get()
    except(DoesNotExist):
        raise BadData()

    try:
        read_state: ReadState = ReadState.objects(ReadState.user_id == user_id, ReadState.channel_id == channel_id).get()
    except(DoesNotExist):
        read_state: ReadState = ReadState.create(user_id=user_id, channel_id=channel_id)
    
    read_state.last_message_id = message.id

    read_state.save()

    return jsonify(to_dict(read_state))
