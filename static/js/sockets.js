const socket = new WebSocket("ws://localhost:5467/ws");

socket.onopen = function (event) {
    console.log("WebSocket connection opened.");
};

socket.onclose = function (event) {
    console.log("WebSocket connection closed.");
};

function handleMediaIsPlaying(mediaId, mediaStatus) {
    const playButton = document.querySelectorAll('[data-media-id="' + mediaId + '"].play-button')[0];

    if (mediaStatus === 'PLAYING') {
        playButton.textContent = 'Stop';
        playButton.classList.remove('stopped');
        playButton.classList.add('playing');
    } else if (mediaStatus === 'STOPPED') {
        playButton.textContent = 'Play';
        playButton.classList.remove('playing');
        playButton.classList.add('stopped');
    }
}

socket.onmessage = function (event) {
    const message = JSON.parse(event.data);
    console.log("New message: " + message);

    if (message.topic === "MediaIsPlayingMessage") {
        handleMediaIsPlaying(message.content.media_id, message.content.status)
    }

    const elementsWithDesiredIp = document.querySelectorAll(`[data-client-ip="${message.ipAddress}"]`);

    elementsWithDesiredIp.forEach((elementWithDesiredIp) => {
        if (message.connected) {
            elementWithDesiredIp.classList.remove("offline-client");
        } else {
            elementWithDesiredIp.classList.add("offline-client");
        }
    });



};