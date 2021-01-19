// Dismiss Registration Error Message
var dismissBtn = document.getElementById('close-btn')
var messageDiv = document.getElementById('registration-message')

if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
        messageDiv.style.display = 'none'
    })
}

// Password fields in registration form
var passwordField = document.getElementById('id_password1')
var helpTextDiv = document.getElementById('help-text-pw')

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
    if (x.style.display == "none" || x.style.display == '') {
      x.style.display = "block"
    } else {
      x.style.display = "none"
    }

    let c = document.getElementById('close-modal')
    c.addEventListener('click', () => {
        x.style.display = "none"
    })
}

// Expand project details in community/labels/projects
function showMore() {
    let div = document.getElementById('proj-expand')

    if (div.style.height == "0px") {
        div.style.height = "300px"
        div.style.transition = "height 0.5s"
    } else {
        div.style.height = "0px"
    }
}

