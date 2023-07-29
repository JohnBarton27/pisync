const socket = new WebSocket("ws://localhost:5467/ws");

socket.onopen = function (event) {
    console.log("WebSocket connection opened.");
};

socket.onclose = function (event) {
    console.log("WebSocket connection closed.");
};

socket.onmessage = function (event) {
    const message = JSON.parse(event.data);
    console.log("New message: " + message.text);
    const elementsWithDesiredIp = document.querySelectorAll(`[data-client-ip="${message.ipAddress}"]`);

    elementsWithDesiredIp.forEach((elementWithDesiredIp) => {
        if (message.connected) {
            elementWithDesiredIp.classList.remove("offline-client");
        } else {
            elementWithDesiredIp.classList.add("offline-client");
        }
    });



};