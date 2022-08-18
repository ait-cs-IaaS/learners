from flask_socketio import emit, join_room
from flask import Blueprint, request
from learners.socketio import socketio

screensharing_api = Blueprint("screensharing_api", __name__)

from engineio.payload import Payload

Payload.max_decode_packets = 500

room = "presentation"
global broadcaster

# TODO: Implement Stop Stream


@socketio.on("register-broadcaster")
def on_register_broadcaster():
    global broadcaster
    broadcaster = request.sid
    join_room(room)


@socketio.on("register-viewer")
def on_register_viewer(user):
    user["id"] = request.sid
    join_room(room)
    emit("new viewer", user, room=broadcaster)


@socketio.on("candidate")
def on_candidate(targetId, event):
    emit("candidate", {"id": request.sid, "event": event}, room=targetId)


@socketio.on("offer")
def on_offer(targetId, event):
    event["broadcaster"]["id"] = broadcaster
    emit("offer", {"broadcaster": event["broadcaster"], "sdp": event["sdp"]}, room=targetId)


@socketio.on("answer")
def on_answer(event):
    emit("answer", {"id": request.sid, "sdp": event["sdp"]}, room=broadcaster)
