//////
// SEARCH CLIENTS MODAL
//////

// Search for Clients Modal
const clientSearchModal = document.getElementById('clientSearchModal');
const closeClientSearchModalBtn = document.getElementById('clientSearchModalClose');
const clientSearchModalHeader = document.getElementById('searchClientsHeader');
const clientSearchConnectBtn = document.getElementById('connectToClientsBtn');

// Close the modal when the close button is clicked
closeClientSearchModalBtn.addEventListener('click', function() {
    clientSearchModal.style.display = 'none';
})

// Close the modal when the user clicks outside of it
window.addEventListener('click', function(event) {
    if (event.target === clientSearchModal) {
        clientSearchModal.style.display = 'none';
    }
});

function search_for_clients() {
    clientSearchModalHeader.textContent = 'Searching for Clients...';
    clientSearchConnectBtn.style.display = 'none';
    let clientListElem = document.getElementById('clientList');
    clientListElem.innerHTML = '';
    clientSearchModal.style.display = 'block';

    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/clients/search', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Handle successful response here
            console.log('Sent request to search for clients!');

            clientSearchModalHeader.textContent = 'Select Client(s) to Add'

            let response = JSON.parse(xhr.response);

            response.clients.forEach(function(client) {
                const listItem = document.createElement('div');
                listItem.className = 'list-item';
                listItem.innerHTML = `
                        <label>
                          <input type="checkbox" value="${client.ip_address}" data-hostname="${client.hostname}" class="client-checkbox">
                          ${client.hostname} (${client.ip_address})
                        </label>`;
                clientListElem.appendChild(listItem);
            });

            clientSearchConnectBtn.style.display = 'block';
        } else {
            // Handle error or other response statuses here
            console.error('Error searching for clients');
        }
    };
    xhr.send(JSON.stringify({}));
}

clientSearchConnectBtn.addEventListener('click', function() {
    let checkedClients = get_checked_clients()
    let requestBody = JSON.stringify({ clients: checkedClients });

    fetch(`/client/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Added clients');
                clientSearchModal.style.display = 'none';

                const clientDisplayListElem = document.getElementById("clientDisplayList");

                response.json().then(data => {
                    data.forEach(function(newClient) {
                        const listItem = document.createElement('div');
                        listItem.className = 'list-item';
                        listItem.innerHTML = `
                                <span>${newClient.friendly_name}</span>
                                <button class="button edit-button">Edit</button>`;
                        clientDisplayListElem.insertBefore(listItem, clientDisplayListElem.firstChild);
                    });
                });

            } else {
                // Handle error
                console.error('Failed to add clients');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

function get_checked_clients() {
    // Get all the client checkboxes
    const clientCheckboxes = document.querySelectorAll('.client-checkbox');

    // Initialize an empty array to store the checked checkboxes
    const checkedClients = [];

    // Iterate through each checkbox
    clientCheckboxes.forEach(checkbox => {
        // Check if the checkbox is checked
        if (checkbox.checked) {
            // Get the value (IP address) of the checked checkbox
            const ipAddress = checkbox.value;
            const hostname = checkbox.getAttribute("data-hostname");

            let client = {
                ip_address: ipAddress,
                hostname: hostname
            }

            // Add the checked IP address to the array
            checkedClients.push(client);
        }
    });

    return checkedClients;
}

//////
// EDIT CLIENT MODAL
//////

// Edit Media Modal Elements
const editClientModal = document.getElementById('editClientModal');
const closeEditClientModalBtn = document.getElementById('editClientModalClose');
const editClientForm = document.getElementById('editClientForm');
//const deleteClientButton = document.getElementById('deleteClientBtn');
let CURRENT_CLIENT_ID = null;
let CURRENT_CLIENT_BUTTON = null;

// Get the buttons that open the edit media modal
let editClientButtons = document.getElementsByClassName('edit-client-btn');

// Form Fields
const EDIT_CLIENT_NAME_INPUT = document.getElementById('clientName');
const EDIT_CLIENT_IP_ADDRESS_INPUT = document.getElementById('clientIp');

// Iterate through all edit buttons
function addListenersForEditClientBtns() {
    editClientButtons = document.getElementsByClassName('edit-client-btn');
    for (let i = 0; i < editClientButtons.length; i++) {
        const editButton = editClientButtons[i];

        // Open Edit Media Modal
        editButton.addEventListener('click', function () {
            CURRENT_CLIENT_BUTTON = this;
            CURRENT_CLIENT_ID = this.getAttribute('data-client-id');
            const clientName = this.getAttribute('data-client-name');
            const clientIp = this.getAttribute('data-client-ip-address');

            // Populate the modal form with client name and IP address
            EDIT_CLIENT_NAME_INPUT.value = clientName;
            EDIT_CLIENT_IP_ADDRESS_INPUT.value = clientIp;

            // Open the modal
            editClientModal.style.display = 'block';
        });
    }
}
addListenersForEditClientBtns();

// Close the modal when the close button is clicked
closeEditClientModalBtn.addEventListener('click', function() {
    editClientModal.style.display = 'none';
});

// Handle form submission
editClientForm.addEventListener('submit', function(event) {
    event.preventDefault();

    // Get data from the form
    const newName = EDIT_CLIENT_NAME_INPUT.value;
    const newIpAddress = EDIT_CLIENT_IP_ADDRESS_INPUT.value;

    const clientUpdateRequest = {
        db_id: CURRENT_CLIENT_ID,
        name: newName,
        ip_address: newIpAddress
    };

    // Create JSON body
    const requestBody = JSON.stringify(clientUpdateRequest);

    // Send PUT request
    fetch(`/client/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: requestBody
    })
        .then(response => {
            if (response.ok) {
                // Handle success
                console.log('Client updated successfully');
                editClientModal.style.display = 'none';

                response.json().then(data => {
                    const nameDisplayElem = document.querySelectorAll('[data-client-id="' + CURRENT_CLIENT_ID + '"].item-name')[0];
                    nameDisplayElem.innerHTML = data.friendly_name;

                    CURRENT_CLIENT_BUTTON.setAttribute('data-client-name', data.friendly_name);
                    CURRENT_CLIENT_BUTTON.setAttribute('data-client-ip-address', data.ip_address);
                });

            } else {
                // Handle error
                console.error('Failed to update client');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});