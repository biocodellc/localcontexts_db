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

// function showMoreTemporary() {
//     let div = document.getElementById('proj-expand')
//     let span = document.getElementById('plus-minus')

//     if (div.style.height == "0px" && span.textContent == "+") {
//         div.style.height = "300px"
//         div.style.transition = "height 0.5s"
//         span.textContent = "-"
//     } else {
//         div.style.height = "0px"
//         span.textContent = "+"
//     }
// }

var provenanceName = 'BC Provenance (BC P)'
var multipleCommunityName = 'BC Multiple Communities (BC MC)'
var openToCollabName = 'BC Open to Collaboration (BC OC)'
var openToCommercializationName = ' BC Open to Commercialization (BC C)'
var researchUseName = 'BC Research Use (BC R)'
var consentVerifiedName = 'BC Consent Verified (BC CV)'

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


// Expand BC Labels Card in Community: Labels
function showBCLabelInfo() {
    let labelContainer = document.getElementById('expand-bclabels')
    let span = document.getElementById('show-more-down')
    let fullCard = document.getElementById('collapsed-card')
    let header = document.getElementById('bclabels-title-vertical')

    if (labelContainer.style.height == "0px") {
        header.style.margin = "0"
        fullCard.style.height = "460px"
        fullCard.style.transition = "height 0.5s"
        labelContainer.style.height = "460px"
        span.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    } else {
        header.style.margin = "auto 0"
        fullCard.style.height = "113px"
        fullCard.style.transition = "height 0.5s"
        labelContainer.style.height = "0px"
        span.innerHTML = `Show More <i class="fa fa-angle-down" aria-hidden="true"></i>`
    }
}

// See more info about each label (Community:Labels)
function expandBCLabel(img) {
    let info = document.getElementById('bclabel-info')
    let fullCard = document.getElementById('collapsed-card')
    let labelContainer = document.getElementById('expand-bclabels')

    if (info.style.height == "0px") {
        labelContainer.style.height = "830px"
        info.style.height = "370px"
        fullCard.style.height = "850px"
    } else {
        labelContainer.style.height = "460px"
        info.style.height = "0px"
        fullCard.style.height = "460px"
    }

    let targetImg = img.id
    let title = document.getElementById('bc-label-title')
    let templateText = document.getElementById('label-template-text')
    let whyUseLabelText = document.getElementById('why-use-this-label')

    switch (targetImg) {
        case 'bcr':
            whichImgClicked('bcr')
            title.textContent = researchUseName
            templateText.textContent = researchUseText
            whyUseLabelText.textContent = researchUse
            break;
        case 'bccv':
            whichImgClicked('bccv')
            title.textContent = consentVerifiedName
            templateText.textContent = consentVerifiedText
            whyUseLabelText.textContent = consentVerifiedUse
            break;
        case 'bcocomm':
            whichImgClicked('bcocomm')
            title.textContent = openToCommercializationName
            templateText.textContent = openToCommercializationText
            whyUseLabelText.textContent = openToCommUse
            break;
        case 'bcocoll':
            whichImgClicked('bcocoll')
            title.textContent = openToCollabName
            templateText.textContent = openToCollabText
            whyUseLabelText.textContent = openToCollabUse
            break;
        case 'bcmc':
            whichImgClicked('bcmc')
            title.textContent = multipleCommunityName
            templateText.textContent = multipleCommunityText
            whyUseLabelText.textContent = multipleCommUse
            break;
        case 'bcp':
            whichImgClicked('bcp')
            title.textContent = provenanceName
            templateText.textContent = provenanceText
            whyUseLabelText.textContent = provenanceUse
            break;
    }

}

//  Assign input value based on which image is selected in Community: Labels
function whichImgClicked(val) {
    var input = document.getElementById('label-value-type')
    input.value = val
}


// Community: Customise labels -- populate default text
var parentDiv = document.getElementById('target-img-div')
if (parentDiv) {
    var image = parentDiv.firstChild.nextSibling
    // console.log(image.id)
    populateTemplate(image.id)
}

function populateTemplate(id) {
    let title = document.getElementById('bclabel-title')
    let templateText = document.getElementById('bclabel-template')

    switch (id) {
        case 'bcr':
            title.value = researchUseName
            templateText.textContent = researchUseText
            break;
        case 'bccv':
            title.value = consentVerifiedName
            templateText.textContent = consentVerifiedText
            break;
        case 'bcocomm':
            title.value = openToCommercializationName
            templateText.textContent = openToCommercializationText
            break;
        case 'bcocoll':
            title.value = openToCollabName
            templateText.textContent = openToCollabText
            break;
        case 'bcmc':
            title.value = multipleCommunityName
            templateText.textContent = multipleCommunityText
            break;
        case 'bcp':
            title.value = provenanceName
            templateText.textContent = provenanceText
            break;
    }

}

// Community: Requests
function showMoreNotice(elem) {
    let noticeID = elem.id
    let expandDiv = document.getElementById(`expand-notice-${noticeID}`)
    let contentCard = document.getElementById(`full-notice-card-${noticeID}`)

    if (expandDiv.style.height == "0px") {
        elem.innerHTML = 'Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>'
        expandDiv.style.height = "auto"
        contentCard.style.height = "auto"
    } else {
        elem.innerHTML = 'Show More <i class="fa fa-angle-down" aria-hidden="true"></i>'
        expandDiv.style.height = "0"
        contentCard.style.height = "201px"
    }
}

// Community: Projects
function showMoreProject(elem) {
    let contribID = elem.id
    let expandDiv = document.getElementById(`expand-contrib-${contribID}`)
    let contentCard = document.getElementById(`full-contrib-card-${contribID}`)

    if (expandDiv.style.height == "0px") {
        elem.innerHTML = 'Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>'
        expandDiv.style.height = "auto"
        contentCard.style.height = "auto"
    } else {
        elem.innerHTML = 'Show More <i class="fa fa-angle-down" aria-hidden="true"></i>'
        expandDiv.style.height = "0"
        contentCard.style.height = "auto"
    }
}

// Community: create project
// Community: requests : apply labels
function displayDefaultText(elem) {
    let isChecked = elem.checked
    let labelID = elem.id

    let matches = labelID.match(/(\d+)/)
    let targetNum = matches[0]

    let targetDiv = document.getElementById(`open-default-text-${targetNum}`)
    let labelName = document.getElementById(`label-name-${targetNum}`)

    if (isChecked) {
        targetDiv.style.height = 'auto'
        labelName.classList.remove('grey-text')
        labelName.classList.add('darkteal-text')
    } else {
        targetDiv.style.height = '0'
        labelName.classList.remove('darkteal-text')
        labelName.classList.add('grey-text')
    }

}

