//////
// ADD CUE MODAL
//////

// Search for Clients Modal
const addCueModal = document.getElementById('addCueModal');
const closeAddCueModalBtn = document.getElementById('addCueModalClose');
const addCueBtn = document.getElementById('addCueBtn');

// Close the modal when the close button is clicked
closeAddCueModalBtn.addEventListener('click', function() {
    addCueModal.style.display = 'none';
})

// Close the modal when the user clicks outside of it
window.addEventListener('click', function(event) {
    if (event.target === addCueModal) {
        addCueModal.style.display = 'none';
    }
});

function open_add_cue_modal() {
    addCueModal.style.display = 'block';
}

// Function to handle form submission
document.getElementById("mediaCueForm").addEventListener("submit", function (event) {
    event.preventDefault();

    // Get form values
    const cueName = document.getElementById("cueName").value;
    const sourceMedia = document.getElementById("sourceMedia").value;
    const sourceMediaTimecode = parseFloat(document.getElementById("sourceMediaTimecode").value);
    const targetMedia = document.getElementById("targetMedia").value;

    const requestBody = JSON.stringify({
        name: cueName,
        sourceMediaId: sourceMedia,
        sourceMediaTimecode: sourceMediaTimecode,
        targetMediaId: targetMedia
    });

    // Send POST request
    fetch(`/cue`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Cue created successfully!');

                // Close Modal
                addCueModal.style.display = 'none';

                response.json().then(data => {
                    // TODO show new cue on HTML page
                    console.log(data)
                });

            } else {
                // Handle error
                console.error('Failed to create cue');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

//////
// EDIT CUE MODAL
//////
const editCueModal = document.getElementById('editCueModal');
const closeEditCueModalBtn = document.getElementById('editCueModalClose');
const editCueForm = document.getElementById('editCueForm');
let CURRENT_CUE_ID = null;
let CURRENT_CUE_BUTTON = null;

// Get the buttons that open the edit media modal
const editCueButtons = document.getElementsByClassName('edit-cue-btn');

// Form Elements
let CUE_NAME_INPUT = document.getElementById('editCueName');
let SRC_MEDIA_INPUT = document.getElementById('editSourceMedia');
let SRC_MEDIA_TIMECODE_INPUT = document.getElementById('editSourceMediaTimecode');
let TARGET_MEDIA_INPUT = document.getElementById('editTargetMedia');

// Iterate through all edit buttons
for (let i = 0; i < editCueButtons.length; i++) {
    const editButton = editCueButtons[i];

    // Open Edit Media Modal
    editButton.addEventListener('click', function() {
        CURRENT_CUE_BUTTON = this;
        CURRENT_CUE_ID = this.getAttribute('data-cue-id');
        const cueName = this.getAttribute('data-cue-name');
        const srcMediaId = this.getAttribute('data-src-media-id');
        const srcMediaTimecode = this.getAttribute('data-src-media-timecode');
        const targetMediaID = this.getAttribute('data-target-media-id');

        // Populate fields
        CUE_NAME_INPUT.value = cueName;
        SRC_MEDIA_INPUT.value = srcMediaId;
        SRC_MEDIA_TIMECODE_INPUT.value = srcMediaTimecode
        TARGET_MEDIA_INPUT.value = targetMediaID;

        // Open the modal
        editCueModal.style.display = 'block';
    });
}

// Close the modal when the close button is clicked
closeEditCueModalBtn.addEventListener('click', function() {
    editCueModal.style.display = 'none';
});

// Close the modal when the user clicks outside of it
window.addEventListener('click', function(event) {
    if (event.target === editCueModal) {
        editCueModal.style.display = 'none';
    }
});

// Handle form submission
editCueForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const cueUpdateRequest = {
        db_id: CURRENT_CUE_ID,
        name: CUE_NAME_INPUT.value,
        source_media_id: SRC_MEDIA_INPUT.value,
        source_media_timecode: SRC_MEDIA_TIMECODE_INPUT.value,
        target_media_id: TARGET_MEDIA_INPUT.value
    }

    // Create JSON body
    const requestBody = JSON.stringify(cueUpdateRequest);

    // Send PUT request
    fetch(`/cue/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Cue updated successfully');
                editCueModal.style.display = 'none';

                response.json().then(data => {
                    // Update data attributes on edit button
                    CURRENT_CUE_BUTTON.setAttribute('data-cue-name', data.name);
                    CURRENT_CUE_BUTTON.setAttribute('data-src-media-id', data.source_media_id);
                    CURRENT_CUE_BUTTON.setAttribute('data-src-media-timecode', data.source_media_timecode_secs);
                    CURRENT_CUE_BUTTON.setAttribute('data-target-media-id', data.target_media_id);

                    // Update display name
                    const nameDisplayElem = document.querySelectorAll('[data-cue-id="' + CURRENT_CUE_ID + '"].item-name')[0];
                    nameDisplayElem.innerHTML = data.name;
                });

            } else {
                // Handle error
                console.error('Failed to update cue');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});