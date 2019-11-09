from flask import current_app, copy_current_request_context, session, request
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room, rooms
from app import socketio

namespace = '/chat'


@socketio.on('testt', namespace=namespace)
def test(message):
    print('testt {}'.format(message))
    emit('server_response',
         {'data': 'Server response!'})
    return 'testk', 3


@socketio.on('connect', namespace=namespace)
def connect():
    print(f'connect {request.sid}')
    emit('server_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request(message):
    print('disconnect')
    emit('server_response',
         {'data': 'Disconnected!'})
    disconnect()

    # todo: unfortunately callback is not called, so I omit this part for a while
    # @copy_current_request_context
    # def can_disconnect():
    #     print('Can disconnect')
    #     disconnect()
    #
    # session['receive_count'] = session.get('receive_count', 0) + 1
    # emit('server_response',
    #      {'data': 'Disconnected!', 'count': session['receive_count']},
    #      callback=can_disconnect)


@socketio.on('join', namespace=namespace)
def join(message):
    print(f"join room: {request.sid}")
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('server_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
             'count': session['receive_count']})


@socketio.on('leave', namespace=namespace)
def leave(message):
    print(f'leave room: {request.sid}')
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('server_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('passs', namespace=namespace)
def passs(message):
    print('pass ' + request.sid)
    emit('server_response', {'data': 'Returned to me', 'huy_v_govne': 'true'}, room=request.sid)


@socketio.on('typing', namespace=namespace)
def typing(message):
    print('typing: ' + request.sid)


@socketio.on('room_message', namespace=namespace)
def send_room_message(message):
    print(f'send room message: {request.sid}')
    session['receive_count'] = session.get('receive_count', 0) + 1
    # todo: check if sender is still in the room. If not -> don't send his message
    emit('server_response',
         {'data': message['message'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('dev_rooms_info', namespace=namespace)
def return_rooms_info(message):
    print(f'dev_rooms_info room: {request.sid}')
    emit('server_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': 5})


if __name__ == '__main__':
    print("if __name__ == '__main__':")
    socketio.run(current_app, debug=True)