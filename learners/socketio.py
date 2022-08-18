from flask_socketio import SocketIO

socketio = SocketIO()


def init_socketio(app):
    global socketio
    socketio.init_app(app)
