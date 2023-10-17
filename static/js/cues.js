function addListenersForEditCueBtns() {
    // Iterate through all edit buttons
    for (let i = 0; i < editCueButtons.length; i++) {
        const editButton = editCueButtons[i];

        // Open Edit Cue Modal
        editButton.addEventListener('click', function() {
            let dataIsEnabled = this.getAttribute('data-is-enabled');
            CURRENT_CUE_BUTTON = this;
            CURRENT_CUE_ID = this.getAttribute('data-cue-id');
            const cueName = this.getAttribute('data-cue-name');
            const srcMediaId = this.getAttribute('data-src-media-id');
            const srcMediaTimecode = this.getAttribute('data-src-media-timecode');
            const targetMediaID = this.getAttribute('data-target-media-id');
            const isEnabled = dataIsEnabled === "True" || dataIsEnabled === true || dataIsEnabled === 'true';

            // Populate fields
            CUE_NAME_INPUT.value = cueName;
            SRC_MEDIA_INPUT.value = srcMediaId;
            SRC_MEDIA_TIMECODE_INPUT.value = srcMediaTimecode
            TARGET_MEDIA_INPUT.value = targetMediaID;
            ENABLED_INPUT.checked = isEnabled;

            // Open the modal
            editCueModal.style.display = 'block';
        });
    }
}

//////
// ADD CUE MODAL
//////

const addCueModal = document.getElementById('addCueModal');
const closeAddCueModalBtn = document.getElementById('addCueModalClose');
const addCueBtn = document.getElementById('addCueBtn');
const cuesListElem = document.getElementById('cuesList');

// Close the modal when the close button is clicked
closeAddCueModalBtn.addEventListener('click', function() {
    addCueModal.style.display = 'none';
})

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
    const targetPattern = document.getElementById("targetPattern").value;

    let requestDict = {
        name: cueName,
        sourceMediaId: sourceMedia,
        sourceMediaTimecode: sourceMediaTimecode
    }

    if (targetMedia) {
        requestDict.targetMediaId = targetMedia;
    }

    if (targetPattern) {
        requestDict.targetPatternId = targetPattern;
    }

    const requestBody = JSON.stringify(requestDict);

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
                    const cueElem = document.createElement('div');
                    cueElem.classList.add('list-item');
                    cuesListElem.appendChild(cueElem);

                    // Name Span
                    const cueNameSpan = document.createElement('span');
                    cueNameSpan.classList.add('item-name');
                    cueNameSpan.setAttribute('data-cue-id', data.db_id);
                    cueNameSpan.innerText = data.name;
                    cueElem.appendChild(cueNameSpan);

                    // Edit Button
                    const cueEditButton = document.createElement('button');
                    cueEditButton.classList.add('button', 'edit-button', 'edit-cue-btn');
                    cueEditButton.setAttribute('data-cue-id', data.db_id);
                    cueEditButton.setAttribute('data-cue-name', data.name);
                    cueEditButton.setAttribute('data-src-media-id', data.source_media_id);
                    cueEditButton.setAttribute('data-src-media-timecode', data.source_media_timecode_secs);
                    cueEditButton.setAttribute('data-target-media-id', data.target_media_id);
                    cueEditButton.setAttribute('data-is-enabled', data.is_enabled);
                    cueEditButton.innerText = 'Edit';
                    cueElem.appendChild(cueEditButton);
                    addListenersForEditCueBtns();
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
let deleteCueBtn = document.getElementById('deleteCueBtn');

// Form Elements
let CUE_NAME_INPUT = document.getElementById('editCueName');
let SRC_MEDIA_INPUT = document.getElementById('editSourceMedia');
let SRC_MEDIA_TIMECODE_INPUT = document.getElementById('editSourceMediaTimecode');
let TARGET_MEDIA_INPUT = document.getElementById('editTargetMedia');
let ENABLED_INPUT = document.getElementById('editEnabled');

addListenersForEditCueBtns();

// Close the modal when the close button is clicked
closeEditCueModalBtn.addEventListener('click', function() {
    editCueModal.style.display = 'none';
});

// Handle form submission
editCueForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const cueUpdateRequest = {
        db_id: CURRENT_CUE_ID,
        name: CUE_NAME_INPUT.value,
        source_media_id: SRC_MEDIA_INPUT.value,
        source_media_timecode: SRC_MEDIA_TIMECODE_INPUT.value,
        target_media_id: TARGET_MEDIA_INPUT.value,
        is_enabled: ENABLED_INPUT.checked
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
                    CURRENT_CUE_BUTTON.setAttribute('data-is-enabled', data.is_enabled);

                    // Update display name
                    const nameDisplayElem = document.querySelectorAll('[data-cue-id="' + CURRENT_CUE_ID + '"].item-name')[0];
                    nameDisplayElem.innerHTML = data.name;

                    if (data.is_enabled && nameDisplayElem.classList.contains('disabled-cue')) {
                        nameDisplayElem.classList.remove('disabled-cue');
                    } else if (!data.is_enabled && !nameDisplayElem.classList.contains('disabled-cue')) {
                        nameDisplayElem.classList.add('disabled-cue');
                    }
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

deleteCueBtn.addEventListener('click', function() {
    fetch(`/cue/${CURRENT_CUE_ID}`, {
        method: 'DELETE'
    }).then(response => {
        if (response.ok) {
            const cueListElem = document.querySelectorAll('[data-cue-id="' + CURRENT_CUE_ID + '"].list-item')[0];
            cueListElem.remove()
        } else {
            console.error('Failed to delete cue!');
        }
    });
});