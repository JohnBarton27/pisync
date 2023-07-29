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
    const elementWithDesiredIp = document.querySelector(`[data-client-ip="${message.ipAddress}"]`);

    if (message.connected) {
        elementWithDesiredIp.classList.remove("offline-client");
        elementWithDesiredIp.textContent = message.name;
    } else {
        elementWithDesiredIp.classList.add("offline-client");
        elementWithDesiredIp.textContent = message.name + " (Offline)";
    }



};