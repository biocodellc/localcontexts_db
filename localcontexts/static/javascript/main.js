// Dismiss Registration Error Message
let dismissBtn = document.getElementById('close-btn')
let messageDiv = document.getElementById('registration-message')

if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
        messageDiv.style.display = 'none'
    })
}

// Password fields in registration form
const passwordField = document.getElementById('id_password1')
const helpTextDiv = document.getElementById('help-text-pw')

if (passwordField ) {
    passwordField.addEventListener('focusin', (event) => {
        helpTextDiv.style.display = 'block' 
      })
    
    passwordField.addEventListener('focusout', (event) => {
        helpTextDiv.style.display = 'none' 
    })
}

// Modal for adding a community member
function addMemberModal() {
    let x = document.getElementById("add-member-modal");
    if (x.style.display === "none") {
      x.style.display = "block";
    } else {
      x.style.display = "none";
    }

    let c = document.getElementById('close-modal')
    c.addEventListener('click', () => {
        x.style.display = "none"
    })
}

