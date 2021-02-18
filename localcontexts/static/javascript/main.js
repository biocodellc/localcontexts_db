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

var provenanceName = '(BC P) Provenance | Ahunga Taketake'
var multipleCommunityName = '(BC MC) Multiple Community BC Label | Hāpori Maha'
var openToCollabName = '(BC OC) Open to Collaboration BC Label | Ka Rata Pea Kia Mahitahi'
var openToCommercializationName = '(BC C) Open to Commercialization BC Label | Ka Rata Pea Kia Whakapakahi'
var researchUseName = '(BC R) Research Use BC Label | Hei Rangahau'
var consentVerifiedName = '(BC CV) Consent Verified BC Label | Whakaaetanga Manatoko'

var provenanceUse = "Indigenous peoples have the right to make decisions about the future use of information, biological collections, data and digital sequence information (DSI) that derives from associated lands, waters and territories. This Label supports the practice of proper and appropriate acknowledgement into the future."
var multipleCommUse = "This Label should be used to indicate that multiple communities have responsibility, custodianship and/or ownership over the geographic regions where this species or biological entity originates/is found. This Label recognizes that whilst one community might exert specific authority, other communities also have rights and responsibilities for use and care."
var openToCollabUse = "This Label is being used to indicate that the community is open to research collaborations and outreach activities. With this Label, future opportunities for collaboration and engagement are supported."
var openToCommUse = "Indigenous peoples have the right to benefit from information, biological collections, data and digital sequence information (DSI) that derives from traditional lands, waters and territories. This Label is being used to indicate the express interest that [community name or authorizing party] has in being a primary party to any future negotiations if future commercialization opportunities arise from these resources."
var researchUse = " This label should be used for permissioning the use of information, collections, data and digital sequence information for unspecified research. The research use label does not give permission for commercialization activities."
var consentVerifiedUse = "Indigenous peoples have the right to permission the use of information, biological collections, data and digital sequence information (DSI) that derives from associated lands, waters and territories. This Label verifies that there are consent conditions in place for uses of information, collections, data and digital sequence information."

var provenanceText = 'This Label is being used to affirm an inherent interest Indigenous people have in the scientific collections and data about communities, peoples, and the biodiversity found within traditional lands, waters and territories. [Community name or authorizing party] has permissioned the use of this collection and associated data for research purposes, and retains the right to be named and associated with it into the future. This association reflects a significant relationship and responsibility to [the species or biological entity] and associated scientific collections and data.'
var multipleCommunityText = 'This Label is being used to affirm responsibility and ownership over this information, collection, data and digital sequence information is spread across several distinct communities. Use will be dependent upon discussion and negotiation with multiple communities.'
var openToCollabText = 'This Label is being used to make clear [community name or authorizing body] is open to future engagement, collaboration, and partnership around research and outreach opportunities.'
var openToCommercializationText = 'This Label is being used to indicate that [community name or authorizing party] is open to commercialization opportunities that might derive from any information, collections, data and DSI to which this Label is connected. As a primary party in any partnership and collaboration opportunities that emerge from the use of these resources, we retain an express interest in any future negotiations.'
var researchUseText = 'This Label is being used by [community name or authorizing body] to allow this information, collection, data and digital sequence information to be used for unspecified research purposes. This Label does not provide permission for commercialization activities.  [Optional return of research results statement].'
var consentVerifiedText = 'This Label is being used to verify that [community name or authorizing party] have consent conditions in place for the use of this information, collections, data and digital sequence information.'


// Default label text -- Attach Labels
function setDefaultText(img) {
    let defaultText = document.getElementById('id_default_text')
    let displayImage = document.getElementById('chosen-label-img')
    let labelHeader = document.getElementById('bc-label-name-h4')
    let hiddenInputName = document.getElementById('pass-name')
    let hiddenInputType = document.getElementById('pass-type')

    let targetImg = img.id
    let source = displayImage.src

    // Find everything in the url after 'bc-labels/bc-' and get the match
    let matches = source.match(/(?<=bc-labels\/bc-).*/)
    let targetStr = matches[0]

    switch (targetImg) {
        case 'bc-research-use-img':
            hiddenInputType.value = 'research'
            hiddenInputName.value = researchUseName
            labelHeader.textContent = researchUseName
            defaultText.textContent = researchUseText
            displayImage.src = source.replace(targetStr, 'research-use.png')
            break;
        case 'bc-consent-verified':
            hiddenInputType.value = 'consent_verified'
            hiddenInputName.value = consentVerifiedName
            labelHeader.textContent = consentVerifiedName
            defaultText.textContent = consentVerifiedText
            displayImage.src = source.replace(targetStr, 'consent-verified.png')
            break;
        case 'bc-open-to-commercialization-img':
            hiddenInputType.value = 'commercialization'
            hiddenInputName.value = openToCommercializationName
            labelHeader.textContent = openToCommercializationName
            defaultText.textContent = openToCommercializationText
            displayImage.src = source.replace(targetStr, 'open-to-commercialization.png')
            break;
        case 'bc-open-to-collaboration-img':
            hiddenInputType.value = 'collaboration'
            hiddenInputName.value = openToCollabName
            labelHeader.textContent = openToCollabName
            defaultText.textContent = openToCollabText
            displayImage.src = source.replace(targetStr, 'open-to-collaboration.png')
            break;
        case 'bc-multiple-community-img':
            hiddenInputType.value = 'multiple_community'
            hiddenInputName.value = multipleCommunityName
            labelHeader.textContent = multipleCommunityName
            defaultText.textContent = multipleCommunityText
            displayImage.src = source.replace(targetStr, 'multiple-community.png')
            break;
        case 'bc-provenance-label-img':
            hiddenInputType.value = 'provenance'
            hiddenInputName.value = provenanceName
            labelHeader.textContent = provenanceName
            defaultText.textContent = provenanceText
            displayImage.src = source.replace(targetStr, 'provenance.png')
            break;
    }
}

// Expand BC Labels Card in Community / Labels
function showBCLabelInfo() {
    let div = document.getElementById('expand-bclabels')
    let span = document.getElementById('show-more-down')
    let card = document.getElementById('collapsed-card')
    let header = document.getElementById('bclabels-title-vertical')

    if (div.style.height == "0px" && span.textContent == "∨") {
        header.style.margin = "0"
        card.style.height = "460px"
        div.style.height = "460px"
        card.style.transition = "height 0.5s"
        span.textContent = "∧"
    } else {
        header.style.margin = "auto 0"
        card.style.height = "113px"
        div.style.height = "0px"
        card.style.transition = "height 0.5s"
        span.textContent = "∨"
    }
}

// See more info about each label
function expandBCLabel(img) {
    let div = document.getElementById('bclabel-info')
    let card = document.getElementById('collapsed-card')
    let imgContainer = document.getElementById('expand-bclabels')

    if (div.style.height == "0px") {
        imgContainer.style.height = "720px"
        div.style.height = "280px"
        card.style.height = "790px"
    } else {
        imgContainer.style.height = "460px"
        div.style.height = "0px"
        card.style.height = "460px"
    }

    let targetImg = img.id
    let templateText = document.getElementById('label-template-text')
    let whyUseLabelText = document.getElementById('why-use-this-label')

    switch (targetImg) {
        case 'bcr':
            templateText.textContent = researchUseText
            whyUseLabelText.textContent = researchUse
            break;
        case 'bccv':
            templateText.textContent = consentVerifiedText
            whyUseLabelText.textContent = consentVerifiedUse
            break;
        case 'bcocomm':
            templateText.textContent = openToCommercializationText
            whyUseLabelText.textContent = openToCommUse
            break;
        case 'bcocoll':
            templateText.textContent = openToCollabText
            whyUseLabelText.textContent = openToCollabUse
            break;
        case 'bcmc':
            templateText.textContent = multipleCommunityText
            whyUseLabelText.textContent = multipleCommUse
            break;
        case 'bcp':
            templateText.textContent = provenanceText
            whyUseLabelText.textContent = provenanceUse
            break;
    }

}


