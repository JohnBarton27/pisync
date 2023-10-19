function addListenersForEditPatternBtns() {
    // Iterate through all edit buttons
    for (let i = 0; i < editPatternButtons.length; i++) {
        const editButton = editPatternButtons[i];

        // Open Edit Cue Modal
        editButton.addEventListener('click', function() {
            CURRENT_PATTERN_BUTTON = this;
            CURRENT_PATTERN_ID = this.getAttribute('data-pattern-id');
            // Populate fields
            PATTERN_NAME_ELEMENT.value = this.getAttribute('data-pattern-name');

            // Open the modal
            editPatternModal.style.display = 'block';
        });
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

                    // TODO add edit button
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
const editPatternModal = document.getElementById('editPatternModal');
const closeEditPatternModalBtn = document.getElementById('editPatternModalClose');
const editPatternForm = document.getElementById('editPatternForm');
let CURRENT_PATTERN_ID = null;
let CURRENT_PATTERN_BUTTON = null;

// Get the buttons that open the edit pattern modal
const editPatternButtons = document.getElementsByClassName('edit-pattern-btn');
let deletePatternBtn = document.getElementById('deletePatternBtn');

// Form Elements
let PATTERN_NAME_ELEMENT = document.getElementById('editPatternName');

addListenersForEditPatternBtns();

// Close the modal when the close button is clicked
closeEditPatternModalBtn.addEventListener('click', function() {
    editPatternModal.style.display = 'none';
});

// Handle form submission
editPatternForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const patternUpdateRequest = {
        db_id: CURRENT_PATTERN_ID,
        name: PATTERN_NAME_ELEMENT.value
    }

    // Create JSON body
    const requestBody = JSON.stringify(patternUpdateRequest);

    // Send PUT request
    fetch(`/ledpattern/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Pattern updated successfully');
                editPatternModal.style.display = 'none';

                response.json().then(data => {
                    // Update data attributes on edit button
                    CURRENT_PATTERN_BUTTON.setAttribute('data-pattern-name', data.name);

                    let displayName = data.name
                    if (data.client) {
                        displayName = `${displayName} (${data.client.friendlyName})`;
                    }
                    // Update display name
                    const nameDisplayElem = document.querySelectorAll('[data-pattern-id="' + CURRENT_PATTERN_ID + '"].item-name')[0];
                    nameDisplayElem.innerHTML = displayName;
                });

            } else {
                // Handle error
                console.error('Failed to update pattern');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

deletePatternBtn.addEventListener('click', function() {
    fetch(`/ledpattern/${CURRENT_PATTERN_ID}`, {
        method: 'DELETE'
    }).then(response => {
        if (response.ok) {
            const patternListElem = document.querySelectorAll('[data-pattern-id="' + CURRENT_PATTERN_ID + '"].list-item')[0];
            patternListElem.remove()
        } else {
            console.error('Failed to delete pattern!');
        }
    });
});