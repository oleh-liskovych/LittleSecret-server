from flask import current_app, copy_current_request_context, session, request
from flask_socketio import SocketIO, emit, disconnect
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
    print('connect {}'.format(request.sid))
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


if __name__ == '__main__':
    print("if __name__ == '__main__':")
    socketio.run(current_app, debug=True)