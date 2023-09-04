const mediaListElem = document.getElementById('mediaList');

//////
// EDIT MEDIA MODAL
//////

// Edit Media Modal Elements
const editMediaModal = document.getElementById('editMediaModal');
const closeEditMediaModalBtn = document.getElementById('editMediaModalClose');
const editMediaForm = document.getElementById('editMediaForm');
const deleteMediaButton = document.getElementById('deleteMediaBtn');
let CURRENT_MEDIA_ID = null;
let CURRENT_MEDIA_BUTTON = null;

// Get the buttons that open the edit media modal
let editButtons = document.getElementsByClassName('edit-media-btn');

// Form Fields
const EDIT_MEDIA_NAME_INPUT = document.getElementById('name');
const EDIT_MEDIA_START_TIME_INPUT = document.getElementById('startMediaTimecode');
const EDIT_MEDIA_END_TIME_INPUT = document.getElementById('endMediaTimecode');

// Iterate through all edit buttons
function addListenersForEditMediaBtns() {
    editButtons = document.getElementsByClassName('edit-media-btn');
    for (let i = 0; i < editButtons.length; i++) {
        const editButton = editButtons[i];

        // Open Edit Media Modal
        editButton.addEventListener('click', function () {
            CURRENT_MEDIA_BUTTON = this;
            CURRENT_MEDIA_ID = this.getAttribute('data-media-id');
            const mediaFilePath = this.getAttribute('data-media-filepath');
            const mediaName = this.getAttribute('data-media-name');
            let mediaStartTime = this.getAttribute('data-media-start');
            let mediaEndTime = this.getAttribute('data-media-end');

            if (mediaStartTime === "None") {
                mediaStartTime = null;
            }

            if (mediaEndTime === "None") {
                mediaEndTime = null;
            }

            // Populate filepath text
            const filepathElem = document.getElementById('editMediaFilepath');
            filepathElem.textContent = mediaFilePath;

            // Populate the modal form with media name and timecode values
            EDIT_MEDIA_NAME_INPUT.value = mediaName;

            if (mediaStartTime) {
                EDIT_MEDIA_START_TIME_INPUT.value = mediaStartTime;
            } else {
                EDIT_MEDIA_START_TIME_INPUT.value = null;
            }

            if (mediaEndTime) {
                EDIT_MEDIA_END_TIME_INPUT.value = mediaEndTime;
            } else {
                EDIT_MEDIA_END_TIME_INPUT.value = null;
            }

            // Open the modal
            editMediaModal.style.display = 'block';
        });
    }
}
addListenersForEditMediaBtns();

// Close the modal when the close button is clicked
closeEditMediaModalBtn.addEventListener('click', function() {
    editMediaModal.style.display = 'none';
});

// Handle form submission
editMediaForm.addEventListener('submit', function(event) {
    event.preventDefault();

    // Get data from the form
    const newName = EDIT_MEDIA_NAME_INPUT.value;
    const startTime = EDIT_MEDIA_START_TIME_INPUT.value;
    const endTime = EDIT_MEDIA_END_TIME_INPUT.value;

    const mediaUpdateRequest = {
        name: newName,
        db_id: CURRENT_MEDIA_ID
    }

    if (startTime.trim() !== '') {
        mediaUpdateRequest.start_time = startTime;
    }

    if (endTime.trim() !== '') {
        mediaUpdateRequest.end_time = endTime;
    }

    // Create JSON body
    const requestBody = JSON.stringify(mediaUpdateRequest);

    // Send PUT request
    fetch(`/media/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Media updated successfully');
                editMediaModal.style.display = 'none';

                response.json().then(data => {
                    const nameDisplayElem = document.querySelectorAll('[data-media-id="' + CURRENT_MEDIA_ID + '"].item-name')[0];
                    nameDisplayElem.innerHTML = data.name;
                    if (data.start_timecode === null) {
                        data.start_timecode = '';
                    }

                    if (data.end_timecode === null) {
                        data.end_timecode = '';
                    }

                    CURRENT_MEDIA_BUTTON.setAttribute('data-media-name', data.name);
                    CURRENT_MEDIA_BUTTON.setAttribute('data-media-filepath', data.file_path);
                    CURRENT_MEDIA_BUTTON.setAttribute('data-media-start', data.start_timecode);
                    CURRENT_MEDIA_BUTTON.setAttribute('data-media-end', data.end_timecode);
                });

            } else {
                // Handle error
                console.error('Failed to update media');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

deleteMediaButton.addEventListener('click', function() {
    fetch(`/media/${CURRENT_MEDIA_ID}`, {
        method: 'DELETE'
    }).then(response => {
        if (response.ok) {
            const mediaListElem = document.querySelectorAll('[data-media-id="' + CURRENT_MEDIA_ID + '"].list-item')[0];
            mediaListElem.remove()
        } else {
            console.error('Failed to delete media!');
        }
    });
});

//////
// PLAY MEDIA
//////
function playMedia(element, id) {
    let xhr = new XMLHttpRequest();
    if (element.classList.contains('stopped')) {
        // Media is stopped, but needs to be played
        xhr.open('POST', '/play/' + id, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Handle successful response here
                console.log('Media played successfully');
            } else {
                // Handle error or other response statuses here
                console.error('Error playing media');
            }
        };
    } else if (element.classList.contains('playing')) {
        // Media is playing, and needs to be stopped
        xhr.open('POST', '/stop/' + id, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Handle successful response here
                console.log('Media stopped successfully');
            } else {
                // Handle error or other response statuses here
                console.error('Error stopping media');
            }
        };
    }
    xhr.send(JSON.stringify({}));
}

//////
// ADD MEDIA MODAL
//////

// Add Media Modal Elements
const addMediaModal = document.getElementById('addMediaModal');
const closeAddMediaModalBtn = document.getElementById('addMediaModalClose');
const addMediaForm = document.getElementById('addMediaForm');
const spinnerElem = document.getElementById('spinnerElem');
const addMediaBtn = document.getElementById('addMediaBtn');
const fileNameDisplayElem = document.getElementById('fileToBeUploadedName');

const MEDIA_FILE_INPUT = document.getElementById('mediaFileInput');
const MEDIA_DESTINATION_INPUT = document.getElementById('destinationClientInput');

// Open Add Media Modal
addMediaBtn.addEventListener('click', function() {
    // Spinner
    addMediaForm.style.display = 'flex';
    spinnerElem.style.display = 'none';

    // Open the modal
    addMediaModal.style.display = 'block';
});

// Close the modal when the close button is clicked
closeAddMediaModalBtn.addEventListener('click', function() {
    addMediaModal.style.display = 'none';
});

// Update file name display when a file is selected
MEDIA_FILE_INPUT.addEventListener("change", () => {
    if (MEDIA_FILE_INPUT.files.length > 0) {
        fileNameDisplayElem.textContent = `${MEDIA_FILE_INPUT.files[0].name}`;
    } else {
        fileNameDisplayElem.textContent = "";
    }
});

// Handle form submission
addMediaForm.addEventListener('submit', function(event) {
    event.preventDefault();
    let isForClient = false;

    // Get data from the form
    const formData = new FormData();
    formData.append("file", MEDIA_FILE_INPUT.files[0]);

    if (MEDIA_DESTINATION_INPUT.value !== 'server') {
        isForClient = true;
        formData.append('client_id', MEDIA_DESTINATION_INPUT.value);
    }

    // Spinner
    addMediaForm.style.display = 'none';
    spinnerElem.style.display = 'flex';


    // Send POST request
    fetch(`/media/upload`, {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Media uploaded successfully');
                addMediaModal.style.display = 'none';

                response.json().then(data => {
                    if (isForClient) {
                        // Allow MediaDumpMessage from client to populate media list
                        return
                    }

                    const mediaElem = document.createElement("div");
                    mediaElem.classList.add("list-item");

                    // Name (text)
                    const nameDisplayElem = document.createElement("span");
                    nameDisplayElem.classList.add("item-name");
                    nameDisplayElem.textContent = data.name;
                    mediaElem.appendChild(nameDisplayElem);

                    // Play Button
                    const playButtonElem = document.createElement('button');
                    playButtonElem.classList.add('button', 'play-button', 'stopped');
                    playButtonElem.onclick = function() {
                        playMedia(playButtonElem, data.db_id);
                    }
                    playButtonElem.setAttribute('data-media-id', data.db_id);
                    playButtonElem.textContent = 'Play';

                    mediaElem.appendChild(playButtonElem);

                    // Edit Button
                    const editButtonElem = document.createElement('button');
                    editButtonElem.classList.add('button', 'edit-button', 'edit-media-btn');
                    editButtonElem.setAttribute('data-media-id', data.db_id);
                    editButtonElem.setAttribute('data-media-name', data.name);
                    editButtonElem.setAttribute('data-media-filepath', data.file_path);
                    editButtonElem.setAttribute('data-media-start','');
                    editButtonElem.setAttribute('data-media-end', '');
                    editButtonElem.textContent = 'Edit';

                    mediaElem.appendChild(editButtonElem);
                    mediaListElem.appendChild(mediaElem);

                    addListenersForEditMediaBtns();
                });

            } else {
                // Handle error
                console.error('Failed to update media');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});