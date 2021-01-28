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

if (togglePassword) {
    togglePassword.addEventListener('click', (e) => {
        var type = password.getAttribute('type') === 'password' ? 'text' : 'password'
        password.setAttribute('type', type)

        togglePassword.classList.toggle('fa-eye-slash')
    })
}

// Toggle Confirm Password Visibility
var togglePassword2 = document.querySelector('#toggle-password2')
var password2 = document.querySelector('#id_password2')

if(togglePassword2) {
    togglePassword2.addEventListener('click', (e) => {
        var type = password2.getAttribute('type') === 'password' ? 'text' : 'password'
        password2.setAttribute('type', type)
    
        togglePassword2.classList.toggle('fa-eye-slash')
    })
}


// Expand project details in researcher:notices
function showMore(elem) {
    let targetId = elem.firstChild.nextSibling.id
    // console.log(targetId)

    let matches = targetId.match(/(\d+)/)
    let targetNum = matches[0]
    // console.log(targetNum)

    let div = document.getElementById(`proj-expand-${targetNum}`)
    let span = document.getElementById(targetId)

    if (div.style.height == "0px" && span.textContent == "+") {
        div.style.height = "300px"
        div.style.transition = "height 0.5s"
        span.textContent = "-"
    } else {
        div.style.height = "0px"
        span.textContent = "+"
    }
}

function showMoreTemporary() {
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

// Default label text
function setDefaultText(img) {
    let defaultText = document.getElementById('bc-label-default-txt')
    let defaultImg = document.getElementById('chosen-label-img')
    let targetImg = img.id
    let source = defaultImg.src

    let matches = source.match(/(?<=bc-labels\/bc-).*/)
    let targetStr = matches[0]
    console.log(source)
    console.log(targetStr)


    const provenanceText = 'This Label is being used to affirm an inherent interest Indigenous people have in the scientific collections and data about communities, peoples, and the biodiversity found within traditional lands, waters and territories. [Community name or authorizing party] has permissioned the use of this collection and associated data for research purposes, and retains the right to be named and associated with it into the future. This association reflects a significant relationship and responsibility to [the species or biological entity] and associated scientific collections and data.'
    const multipleCommunityText = 'This Label is being used to affirm responsibility and ownership over this information, collection, data and digital sequence information is spread across several distinct communities. Use will be dependent upon discussion and negotiation with multiple communities.'
    const openToCollabText = 'This Label is being used to make clear [community name or authorizing body] is open to future engagement, collaboration, and partnership around research and outreach opportunities.'
    const openToCommercializationText = 'This Label is being used to indicate that [community name or authorizing party] is open to commercialization opportunities that might derive from any information, collections, data and DSI to which this Label is connected. As a primary party in any partnership and collaboration opportunities that emerge from the use of these resources, we retain an express interest in any future negotiations.'
    const researchUseText = 'This Label is being used by [community name or authorizing body] to allow this information, collection, data and digital sequence information to be used for unspecified research purposes. This Label does not provide permission for commercialization activities.  [Optional return of research results statement].'
    const consentVerified = 'This Label is being used to verify that [community name or authorizing party] have consent conditions in place for the use of this information, collections, data and digital sequence information.'

    switch (targetImg) {
        case 'bc-research-use-img':
            defaultText.textContent = researchUseText
            defaultImg.src = source.replace(targetStr, 'research-use.png')
            break;
        case 'bc-consent-verified':
            defaultText.textContent = consentVerified
            defaultImg.src = source.replace(targetStr, 'consent-verified.png')
            break;
        case 'bc-open-to-commercialization-img':
            defaultText.textContent = openToCommercializationText
            defaultImg.src = source.replace(targetStr, 'open-to-commercialization.png')
            break;
        case 'bc-open-to-collaboration-img':
            defaultText.textContent = openToCollabText
            defaultImg.src = source.replace(targetStr, 'open-to-collaboration.png')
            break;
        case 'bc-multiple-community-img':
            defaultText.textContent = multipleCommunityText
            defaultImg.src = source.replace(targetStr, 'multiple-community.png')
            break;
        case 'bc-provenance-label-img':
            defaultText.textContent = provenanceText
            defaultImg.src = source.replace(targetStr, 'provenance.png')
            break;
    }
}



