//////
// EDIT MEDIA MODAL
//////

// Edit Media Modal Elements
const editMediaModal = document.getElementById('editMediaModal');
const closeEditMediaModalBtn = document.getElementById('editMediaModalClose');
const editMediaForm = document.getElementById('editMediaForm');
let CURRENT_MEDIA_ID = null;
let CURRENT_MEDIA_BUTTON = null;

// Get the buttons that open the edit media modal
const editButtons = document.getElementsByClassName('edit-media-btn');

// Form Fields
const EDIT_MEDIA_NAME_INPUT = document.getElementById('name');
const EDIT_MEDIA_START_TIME_INPUT = document.getElementById('startMediaTimecode');
const EDIT_MEDIA_END_TIME_INPUT = document.getElementById('endMediaTimecode');

// Iterate through all edit buttons
for (let i = 0; i < editButtons.length; i++) {
    const editButton = editButtons[i];

    // Open Edit Media Modal
    editButton.addEventListener('click', function() {
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

// Close the modal when the close button is clicked
closeEditMediaModalBtn.addEventListener('click', function() {
    editMediaModal.style.display = 'none';
});

// Close the modal when the user clicks outside of it
window.addEventListener('click', function(event) {
    if (event.target === editMediaModal) {
        editMediaModal.style.display = 'none';
    }
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