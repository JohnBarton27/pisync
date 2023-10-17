function addListenersForEditPatternBtns() {
    // Iterate through all edit buttons
    for (let i = 0; i < editPatternButtons.length; i++) {
        const editButton = editPatternButtons[i];

        // // Open Edit Cue Modal
        // editButton.addEventListener('click', function() {
        //     CURRENT_PATTERN_BUTTON = this;
        //     CURRENT_PATTERN_ID = this.getAttribute('data-pattern-id');
        //     const patternName = this.getAttribute('data-pattern-name');
        //
        //     // Populate fields
        //     PATTERN_NAME_ELEMENT.value = patternName;
        //
        //     // Open the modal
        //     editPatternModal.style.display = 'block';
        // });
    }
}

//////
// ADD PATTERN MODAL
//////
const addPatternModal = document.getElementById('addPatternModal');
const closeAddPatternModalBtn = document.getElementById('addPatternModalClose');
const addPatternBtn = document.getElementById('addPatternBtn');
const patternsListElem = document.getElementById('ledPatternsList');

// Close the modal when the close button is clicked
closeAddPatternModalBtn.addEventListener('click', function() {
    addCueModal.style.display = 'none';
})

function open_add_pattern_modal() {
    addPatternModal.style.display = 'block';
}

// Function to handle form submission
document.getElementById("addPatternForm").addEventListener("submit", function (event) {
    event.preventDefault();

    // Get form values
    const patternName = document.getElementById("patternName").value;
    const patternClientId = document.getElementById("patternClientId").value;

    const requestBody = JSON.stringify({
        name: patternName,
        client_id: patternClientId
    });

    // Send POST request
    fetch(`/ledpattern`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Pattern created successfully!');

                // Close Modal
                addPatternModal.style.display = 'none';

                response.json().then(data => {
                    const patternElem = document.createElement('div');
                    patternElem.classList.add('list-item');
                    patternsListElem.appendChild(patternElem);

                    // Name Span
                    const patternNameSpan = document.createElement('span');
                    patternNameSpan.classList.add('item-name');
                    patternNameSpan.setAttribute('data-pattern-id', data.db_id);
                    patternNameSpan.innerText = data.name;
                    patternElem.appendChild(patternNameSpan);

                    // Edit Button
                    const patternEditButton = document.createElement('button');
                    patternEditButton.classList.add('button', 'edit-button', 'edit-pattern-btn');
                    patternEditButton.setAttribute('data-pattern-id', data.db_id);
                    patternEditButton.setAttribute('data-pattern-name', data.name);
                    patternEditButton.innerText = 'Edit';
                    patternElem.appendChild(patternEditButton);
                    addListenersForEditPatternBtns();
                });

            } else {
                // Handle error
                console.error('Failed to create pattern');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

function playLedPattern(pattern_id) {
    fetch(`/ledpatterns/play/${pattern_id}`, {
        method: 'POST'
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Pattern played successfully!');
            } else {
                // Handle error
                console.error('Failed to play pattern');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

//////
// EDIT PATTERN MODAL
//////
// const editCueModal = document.getElementById('editCueModal');
// const closeEditCueModalBtn = document.getElementById('editCueModalClose');
// const editCueForm = document.getElementById('editCueForm');
let CURRENT_PATTERN_ID = null;
let CURRENT_PATTERN_BUTTON = null;
//
// // Get the buttons that open the edit media modal
const editPatternButtons = document.getElementsByClassName('edit-pattern-btn');
// let deleteCueBtn = document.getElementById('deleteCueBtn');
//
// // Form Elements
//let PATTERN_NAME_ELEMENT = document.getElementById('editPatternName');
// let SRC_MEDIA_INPUT = document.getElementById('editSourceMedia');
// let SRC_MEDIA_TIMECODE_INPUT = document.getElementById('editSourceMediaTimecode');
// let TARGET_MEDIA_INPUT = document.getElementById('editTargetMedia');
// let ENABLED_INPUT = document.getElementById('editEnabled');
//
// addListenersForEditCueBtns();
//
// // Close the modal when the close button is clicked
// closeEditCueModalBtn.addEventListener('click', function() {
//     editCueModal.style.display = 'none';
// });
//
// // Handle form submission
// editCueForm.addEventListener('submit', function(event) {
//     event.preventDefault();
//
//     const cueUpdateRequest = {
//         db_id: CURRENT_CUE_ID,
//         name: CUE_NAME_INPUT.value,
//         source_media_id: SRC_MEDIA_INPUT.value,
//         source_media_timecode: SRC_MEDIA_TIMECODE_INPUT.value,
//         target_media_id: TARGET_MEDIA_INPUT.value,
//         is_enabled: ENABLED_INPUT.checked
//     }
//
//     // Create JSON body
//     const requestBody = JSON.stringify(cueUpdateRequest);
//
//     // Send PUT request
//     fetch(`/cue/update`, {
//         method: 'PUT',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: requestBody
//     })
//         .then(response => {
//             if (response.ok) {
//                 // Handle success
//                 console.log('Cue updated successfully');
//                 editCueModal.style.display = 'none';
//
//                 response.json().then(data => {
//                     // Update data attributes on edit button
//                     CURRENT_CUE_BUTTON.setAttribute('data-cue-name', data.name);
//                     CURRENT_CUE_BUTTON.setAttribute('data-src-media-id', data.source_media_id);
//                     CURRENT_CUE_BUTTON.setAttribute('data-src-media-timecode', data.source_media_timecode_secs);
//                     CURRENT_CUE_BUTTON.setAttribute('data-target-media-id', data.target_media_id);
//                     CURRENT_CUE_BUTTON.setAttribute('data-is-enabled', data.is_enabled);
//
//                     // Update display name
//                     const nameDisplayElem = document.querySelectorAll('[data-cue-id="' + CURRENT_CUE_ID + '"].item-name')[0];
//                     nameDisplayElem.innerHTML = data.name;
//
//                     if (data.is_enabled && nameDisplayElem.classList.contains('disabled-cue')) {
//                         nameDisplayElem.classList.remove('disabled-cue');
//                     } else if (!data.is_enabled && !nameDisplayElem.classList.contains('disabled-cue')) {
//                         nameDisplayElem.classList.add('disabled-cue');
//                     }
//                 });
//
//             } else {
//                 // Handle error
//                 console.error('Failed to update cue');
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
// });
//
// deleteCueBtn.addEventListener('click', function() {
//     fetch(`/cue/${CURRENT_CUE_ID}`, {
//         method: 'DELETE'
//     }).then(response => {
//         if (response.ok) {
//             const cueListElem = document.querySelectorAll('[data-cue-id="' + CURRENT_CUE_ID + '"].list-item')[0];
//             cueListElem.remove()
//         } else {
//             console.error('Failed to delete cue!');
//         }
//     });
// });