//////
// EDIT MEDIA MODAL
//////

// Edit Media Modal Elements
const editMediaModal = document.getElementById('editMediaModal');
const closeEditMediaModalBtn = document.getElementById('editMediaModalClose');
const editMediaForm = document.getElementById('editMediaForm');
let CURRENT_MEDIA_ID = null;

// Get the buttons that open the edit media modal
const editButtons = document.getElementsByClassName('edit-media-btn');

// Iterate through all edit buttons
for (let i = 0; i < editButtons.length; i++) {
    const editButton = editButtons[i];

    // Open Edit Media Modal
    editButton.addEventListener('click', function() {
        CURRENT_MEDIA_ID = this.getAttribute('data-media-id');
        const mediaFilePath = this.getAttribute('data-media-filepath')
        const mediaName = this.getAttribute('data-media-name');

        // Populate filepath text
        const filepathElem = document.getElementById('editMediaFilepath');
        filepathElem.textContent = mediaFilePath;

        // Populate the modal form with media name
        const nameInput = document.getElementById('name');
        nameInput.value = mediaName;

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

    // Fetch media ID and name from the form
    const nameInput = document.getElementById('name');
    const newName = nameInput.value;

    // Create JSON body
    const requestBody = JSON.stringify({ name: newName, db_id: CURRENT_MEDIA_ID });

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
function playMedia(id) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/play/' + id, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Handle successful response here
            console.log('Media played successfully');
        } else {
            // Handle error or other response statuses here
            console.error('Error playing media');
        }
    };
    xhr.send(JSON.stringify({}));
}