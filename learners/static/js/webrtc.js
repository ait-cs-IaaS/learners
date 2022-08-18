// getting dom elements
const sharingActionContainer = document.getElementById("sharingActionContainer");
const btnStartScreenSharing = document.getElementById("btnStartScreenSharing");
const btnStopScreenSharing = document.getElementById("btnStopScreenSharing");
const btnWatch = document.getElementById("btnWatch");
const statusDiv = document.getElementById("statusDiv");
const controlsDiv = document.getElementById("controls");
const videoElement = document.querySelector("video");

// variables
let user;
let rtcPeerConnections = {};
let stream

// constants
const iceServers = {
  iceServers: [
    // { urls: "stun:stun.services.mozilla.com" },
    // { urls: "stun:stun.l.google.com:19302" },
    // {
    //   urls: 'turn:' + TURN_SERVER_URL + '?transport=tcp',
    //   username: TURN_SERVER_USERNAME,
    //   credential: TURN_SERVER_CREDENTIAL
    // },
    // {
    //   urls: 'turn:' + TURN_SERVER_URL + '?transport=udp',
    //   username: TURN_SERVER_USERNAME,
    //   credential: TURN_SERVER_CREDENTIAL
    // }
  ],
};
const streamConstraints = { audio: false, video: { height: 480 } };

// socketio
var protocol = window.location.protocol;
var socket = io(protocol + '//' + document.domain + ':' + location.port, { autoConnect: false });

if (btnStartScreenSharing) {
  btnStartScreenSharing.onclick = function () {
    user = {
      room: 'presentation',
      name: 'broadcaster'
    };

    var constraints = { video: { frameRate: { ideal: 5, max: 10 } } };

    navigator.mediaDevices
      .getDisplayMedia(constraints)
      .then(function (localStream) {
        videoElement.classList.add("local-video");
        stream = localStream
        videoElement.srcObject = stream;
        socket.connect()
        socket.emit("register-broadcaster");
      })
      .catch(function (err) {
        console.log("An error ocurred when accessing media devices", err);
      });
  };
}

if (btnWatch) {
  btnWatch.onclick = function () {
    socket.connect()
    user = {
      room: 'presentation',
      name: uuidv4()
    };

    socket.emit("register-viewer", user);
  };
}

// message handlers
socket.on("new viewer", function (viewer) {

  rtcPeerConnections[viewer.id] = new RTCPeerConnection(iceServers);

  if (user.name === 'broadcaster') {
    stream
      .getTracks()
      .forEach((track) => rtcPeerConnections[viewer.id].addTrack(track, stream));
  }

  rtcPeerConnections[viewer.id].onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit("candidate", viewer.id, {
        type: "candidate",
        label: event.candidate.sdpMLineIndex,
        id: event.candidate.sdpMid,
        candidate: event.candidate.candidate,
      });
    }
  }

  rtcPeerConnections[viewer.id]
    .createOffer({ offerToReceiveVideo: true })
    .then((sessionDescription) => {
      rtcPeerConnections[viewer.id].setLocalDescription(sessionDescription);
      socket.emit("offer", viewer.id, {
        type: "offer",
        sdp: sessionDescription,
        broadcaster: { name: 'broadcaster' },
      });
    })
    .catch((error) => {
      console.log(error);
    });

});

socket.on("candidate", function (data) {
  var candidate = new RTCIceCandidate({
    sdpMLineIndex: data.event.label,
    candidate: data.event.candidate,
  });
  rtcPeerConnections[data.id].addIceCandidate(candidate);
});

socket.on("offer", function (data) {

  broadcaster = data.broadcaster
  sdp = data.sdp

  rtcPeerConnections[broadcaster.id] = new RTCPeerConnection(iceServers);
  rtcPeerConnections[broadcaster.id].setRemoteDescription(sdp);

  rtcPeerConnections[broadcaster.id]
    .createAnswer({ offerToReceiveVideo: true })
    .then((sessionDescription) => {
      rtcPeerConnections[broadcaster.id].setLocalDescription(
        sessionDescription
      );
      socket.emit("answer", {
        type: "answer",
        sdp: sessionDescription,
        room: 'presentation',
      });
    });

  rtcPeerConnections[broadcaster.id].ontrack = (event) => {
    let remoteStream = event.streams[0]
    videoElement.srcObject = remoteStream;
  };

  rtcPeerConnections[broadcaster.id].onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit("candidate", broadcaster.id, {
        type: "candidate",
        label: event.candidate.sdpMLineIndex,
        id: event.candidate.sdpMid,
        candidate: event.candidate.candidate,
      });
    }
  };

  videoElement.classList.add("remote-video");
});

socket.on("answer", function (data) {
  rtcPeerConnections[data.id].setRemoteDescription(
    new RTCSessionDescription(data.sdp)
  );

  videoElement.classList.add("local-video");
  statusDiv.style = "display: block;";
  controlsDiv.classList.add("streaming");
  if (btnStartScreenSharing) btnStartScreenSharing.style = "display: none;";
  if (btnStopScreenSharing) btnStopScreenSharing.style = "display: block;";
});

function uuidv4() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}
