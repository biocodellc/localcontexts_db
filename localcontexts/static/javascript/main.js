// Dismiss Messages
var dismissBtn = document.getElementById('close-btn')
var messageDiv = document.getElementById('alert-message')

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

// Registration Page
// Toggle Password Visibility
var togglePassword = document.querySelector('#toggle-password')
var password = document.querySelector('#id_password1')

togglePassword.addEventListener('click', (e) => {
    var type = password.getAttribute('type') === 'password' ? 'text' : 'password'
    password.setAttribute('type', type)

    togglePassword.classList.toggle('fa-eye-slash')
})

// Toggle Confirm Password Visibility
var togglePassword2 = document.querySelector('#toggle-password2')
var password2 = document.querySelector('#id_password2')

togglePassword2.addEventListener('click', (e) => {
    var type = password2.getAttribute('type') === 'password' ? 'text' : 'password'
    password2.setAttribute('type', type)

    togglePassword2.classList.toggle('fa-eye-slash')
})

// Expand project details in community/labels/projects
function showMore() {
    let div = document.getElementById('proj-expand')
    let span = document.getElementById('plus-minus')

    if (div.style.height == "0px" && span.textContent == "+") {
        div.style.height = "300px"
        div.style.transition = "height 0.5s"
        span.textContent = "-"
    } else {
        div.style.height = "0px"
        span.textContent = "+"
    }
}

