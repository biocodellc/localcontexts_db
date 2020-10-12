// Dismiss Registration Error Message
let dismissBtn = document.getElementById('close-btn')
let messageDiv = document.getElementById('registration-message')

dismissBtn.addEventListener('click', () => {
    messageDiv.style.display = 'none'
})