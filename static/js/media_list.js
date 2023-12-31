function getCurrentPlayButtonsObjects() {
    let playBtns = {};
    let playButtonElems = document.querySelectorAll('#mediaList .list-item .play-button');

    playButtonElems.forEach(function(playElem) {
        let currentClass = 'playing';
        if (playElem.classList.contains('stopped')) {
            currentClass = 'stopped';
        }
        playBtns[parseInt(playElem.getAttribute('data-media-id'))] = currentClass;
    });

    return playBtns;
}

function getClientObjects() {
    let clientElems = document.querySelectorAll('#clientDisplayList .list-item span');

    let clients = [];

    clientElems.forEach(function(client) {
        let client_dict = {
            id: parseInt(client.getAttribute('data-client-id')),
            ipAddress: client.getAttribute('data-client-ip'),
            friendlyName: client.innerText,
            isOffline: client.classList.contains('offline-client')
        };

        clients.push(client_dict);

    });
    return clients;
}

function getClientById(clientList, clientId) {
    for (const client of clientList) {
        if (client.id === clientId) {
            return client;
        }
    }
}

function buildMediaList(mediaList) {
    let clientObjects = getClientObjects();
    let playButtonStatuses = getCurrentPlayButtonsObjects();

    // Clear out mediaListElem
    mediaListElem.innerHTML = '';

    mediaList.forEach(function(media) {
        let playingClass = playButtonStatuses[media.db_id];
        if (playingClass === null || playingClass === undefined) {
            playingClass = 'stopped';
        }
        const thisClient = getClientById(clientObjects, media.client_id);
        const listElem = document.createElement('div');
        listElem.classList.add('list-item');
        listElem.setAttribute('data-media-id', media.db_id);
        mediaListElem.appendChild(listElem);

        // Display Name
        const nameSpan = document.createElement('span');
        nameSpan.classList.add('item-name');
        if (media.client_id && thisClient.isOffline) {
            nameSpan.classList.add('offline-client');
        }
        nameSpan.setAttribute('data-media-id', media.db_id);

        if (media.client_id) {
            nameSpan.setAttribute('data-client-ip', thisClient.ipAddress);
        }

        let innerText = media.name;

        if (media.client_id) {
            innerText += ` (${thisClient.friendlyName})`;
        }

        nameSpan.innerText = innerText;
        listElem.appendChild(nameSpan);

        // Play Button
        let playBtn = document.createElement('button');
        playBtn.classList.add('button', 'play-button', playingClass);
        playBtn.onclick = function() {
            playMedia(playBtn, media.db_id);
        }
        playBtn.setAttribute('data-media-id', media.db_id);
        if (playingClass === 'playing') {
            playBtn.innerText = 'Stop';
        } else {
            playBtn.innerText = 'Play';
        }
        listElem.appendChild(playBtn);

        // Edit Button
        let start = media.start_timecode;
        if (start === null) {
            start = '';
        }
        let end = media.end_timecode;
        if (end === null) {
            end = '';
        }
        let editBtn = document.createElement('button');
        editBtn.classList.add('button', 'edit-button', 'edit-media-btn');
        editBtn.setAttribute('data-media-id', media.db_id);
        editBtn.setAttribute('data-media-name', media.name);
        editBtn.setAttribute('data-media-filepath', media.file_path);
        editBtn.setAttribute('data-media-start', start);
        editBtn.setAttribute('data-media-end', end);
        editBtn.innerText = 'Edit';
        listElem.appendChild(editBtn)
    });

    addListenersForEditMediaBtns();
}