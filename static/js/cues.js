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