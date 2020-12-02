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
passwordField.addEventListener('focusin', (event) => {
    helpTextDiv.style.display = 'block' 
  })

passwordField.addEventListener('focusout', (event) => {
    helpTextDiv.style.display = 'none' 
})