// Dismiss Messages
var dismissBtn = document.getElementById('close-btn')
var messageDiv = document.getElementById('alert-message')

if (dismissBtn) { dismissBtn.addEventListener('click', () => { messageDiv.style.display = 'none'}) }

// Password fields in registration form
var passwordField = document.getElementById('id_password1')
var helpTextDiv = document.getElementById('help-text-pw')

if (passwordField) {
    passwordField.addEventListener('focusin', (event) => { helpTextDiv.style.display = 'block' })
    passwordField.addEventListener('focusout', (event) => { helpTextDiv.style.display = 'none' })
}

// Show customized label text in community: labels
function customText(imgDiv) {
    let labelID = imgDiv.id
    let divs = Array.from(document.querySelectorAll('.div-toggle'))
    // console.log(labelID)

    divs.forEach(div => { if (div.id.includes(labelID) && div.style.height == '0px') { div.style.height = 'auto' } else { div.style.height = '0px' } })

    // Toggle text color based on what Label is selected
    let pDivs = Array.from(document.querySelectorAll('.toggle-txt-color'))
    pDivs.forEach(node => {
        let nodeID = node.id
        if (nodeID.includes(labelID)) { node.classList.replace('grey-text', 'darkteal-text') } else { node.classList.replace('darkteal-text', 'grey-text') }
    })
}

async function fetchLabels(type) {
    const response = await fetch('/static/json/Labels.json')
    const data = await response.json()
    if (type == 'bc') { return data.bcLabels } else if (type == 'tk') { return data.tkLabels } else if (type == 'both') { return data }
}

// Expand BC Labels Card in Community: Labels -> select-labels
function showBCLabelInfo() {
    let labelContainer = document.getElementById('expand-bclabels')
    let span = document.getElementById('show-more-down')
    let fullCard = document.getElementById('collapsed-card')
    let header = document.getElementById('bclabels-title-vertical')

    if (labelContainer.style.height == "0px") {
        header.style.margin = "0"
        fullCard.style.height = "auto"
        labelContainer.style.height = "auto"
        span.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    } else {
        header.style.margin = "auto 0"
        fullCard.style.height = "113px"
        // fullCard.style.transition = "height 0.5s"
        labelContainer.style.height = "0px"
        span.innerHTML = `Show More <i class="fa fa-angle-down" aria-hidden="true"></i>`
    }
}

// See more info about each label (Community:Labels)
function expandBCLabel(img) {

    // Toggle selected Label color 
    let txtDivs = Array.from(document.querySelectorAll('.toggle-txt-color'))
    txtDivs.forEach(node => { if (node == img.parentElement.nextElementSibling) { node.classList.replace('grey-text', 'darkteal-text') } else { node.classList.replace('darkteal-text', 'grey-text') } })

    let targetImg = img.id

    // Provenance
    let infoProv = document.getElementById('bclabel-info-prov')
    let titleProv = document.getElementById('bc-label-title-prov')
    let templateTextProv = document.getElementById('label-template-text-bc-prov')
    let whyUseLabelTextProv = document.getElementById('why-use-this-label-bc-prov')

    // Protocols
    let infoProt = document.getElementById('bclabel-info-prot')
    let titleProt = document.getElementById('bc-label-title-prot')
    let templateTextProt = document.getElementById('label-template-text-bc-prot')
    let whyUseLabelTextProt = document.getElementById('why-use-this-label-bc-prot')

    // Permissions
    let infoPerms = document.getElementById('bclabel-info-perm')
    let titlePerms = document.getElementById('bc-label-title-perm')
    let templateTextPerms = document.getElementById('label-template-text-bc-perm')
    let whyUseLabelTextPerms = document.getElementById('why-use-this-label-bc-perm')

    // Hidden Inputs
    let inputProv = document.getElementById('bc-label-value-type-prov')
    let inputProt = document.getElementById('bc-label-value-type-prot')
    let inputPerms = document.getElementById('bc-label-value-type-perm')

    fetchLabels('bc').then(populateBCLabel)

    // Set content based on which Label was selected
    function populateBCLabel(data) {
        data.forEach(bclabel => {
            if (bclabel.labelCode == targetImg) { 
                displayExpandedImage(targetImg)
                checkLabelExists(bclabel, targetImg, 'BC')

                if (bclabel.labelCategory == 'protocol') {
                    openLabelInfoDiv(infoProt, infoProv, infoPerms)
                    //  Assign input value based on which bc label image is selected
                    inputProt.value = targetImg
                    titleProt.textContent = bclabel.labelName
                    templateTextProt.textContent = bclabel.labelDefaultText
                    whyUseLabelTextProt.textContent = bclabel.whyUseThisLabel  
                
                } else if (bclabel.labelCategory == 'provenance') {
                    openLabelInfoDiv(infoProv, infoProt, infoPerms)
                    inputProv.value = targetImg
                    titleProv.textContent = bclabel.labelName
                    templateTextProv.textContent = bclabel.labelDefaultText
                    whyUseLabelTextProv.textContent = bclabel.whyUseThisLabel

                } else if (bclabel.labelCategory == 'permission') {
                    openLabelInfoDiv(infoPerms, infoProt, infoProv)
                    inputPerms.value = targetImg
                    titlePerms.textContent = bclabel.labelName
                    templateTextPerms.textContent = bclabel.labelDefaultText
                    whyUseLabelTextPerms.textContent = bclabel.whyUseThisLabel
                }
            }
        })
    }

}

// Will disable "customize Label" btn if Label exists (select-labels)
function checkLabelExists(label, selectedLabelCode, labelType) {
    let btnTKProv = document.getElementById(`btn${labelType}Prov`)
    let btnTKProt = document.getElementById(`btn${labelType}Prot`)
    let btnTKPerms = document.getElementById(`btn${labelType}Perms`)

    // Takes all hidden inputs with the label_type of labels that have already been created by the community
    let inputs = Array.from(document.querySelectorAll(`.check${labelType}LabelType`))
    let values = []
    inputs.forEach(input => values.push(input.value))

    if (label.labelCode == selectedLabelCode) {
        if (values.includes(label.labelType)) {
            if (label.labelCategory == 'provenance') {
                btnTKProv.setAttribute("disabled","disabled")
                btnTKProv.classList.replace('action-btn', 'disabled-btn')
            } else if (label.labelCategory == 'protocol') {
                btnTKProt.setAttribute("disabled","disabled")
                btnTKProt.classList.replace('action-btn', 'disabled-btn')
            } else if (label.labelCategory == 'permission') {
                btnTKPerms.setAttribute("disabled","disabled")
                btnTKPerms.classList.replace('action-btn', 'disabled-btn')
            }
        }  else {
            if (label.labelCategory == 'provenance') {
                btnTKProv.removeAttribute("disabled")
                btnTKProv.classList.replace('disabled-btn', 'action-btn')
            } else if (label.labelCategory == 'protocol') {
                btnTKProt.removeAttribute("disabled")
                btnTKProt.classList.replace('disabled-btn', 'action-btn')
            } else if (label.labelCategory == 'permission') {
                btnTKPerms.removeAttribute("disabled")
                btnTKPerms.classList.replace('disabled-btn', 'action-btn')
            }
        }
    }
}

// Display Label images that was clicked in the expanded Div
function displayExpandedImage(labelCode) {
    let imgArray

    if (labelCode.startsWith('b')) {
        imgArray = Array.from(document.querySelectorAll('.bc-img-div'))
    } else if (labelCode.startsWith('t')) {
        imgArray = Array.from(document.querySelectorAll('.tk-img-div'))
    }

    for (let i = 0; i < imgArray.length; i ++) {
        // take the id and split it, compare labelCode to the split
        if (imgArray[i].id.slice(21) == labelCode) { imgArray[i].classList.replace('hide', 'show') } else { imgArray[i].classList.replace('show', 'hide') }
    }
}

// Community: Customize labels -- populate default text
var parentDiv = document.getElementById('target-img-div')
if (parentDiv) {
    var image = parentDiv.firstChild.nextSibling
    populateTemplate(image.id)
}

function populateTemplate(id) {
    let templateText = document.getElementById('label-template-text')
    let hiddenInput = document.getElementById('input-label-name')
    let whyUseText = document.getElementById('whyUseText')

    fetchLabels('both').then(populate)

    function populate(data) {
        if (id.startsWith('b')) {
            let bclabels = data.bcLabels
            bclabels.forEach(bclabel => {
                if (id == bclabel.labelCode) {
                    whyUseText.textContent = bclabel.whyUseThisLabel
                    hiddenInput.value = bclabel.labelName
                    templateText.textContent = bclabel.labelDefaultText
                }
            })
        } else if (id.startsWith('t')) {
            let tklabels = data.tkLabels
            tklabels.forEach(tklabel => {
                if (id == tklabel.labelCode) {
                    whyUseText.textContent = tklabel.whyUseThisLabel
                    hiddenInput.value = tklabel.labelName
                    templateText.textContent = tklabel.labelDefaultText
                }
            })
        }
    }

}

// Approve Label: show note div
if (window.location.href.includes('community/labels/')) {
    let noBtn = document.getElementById('displayLabelNote')
    noBtn.addEventListener('click', (e) => {
        e.preventDefault()
        let div = document.getElementById('labelNoteDiv')
        div.classList.remove('hide')
        div.classList.add('show')
    })

    let closeNoteDivBtn = document.getElementById('closeNoteDiv')
    closeNoteDivBtn.addEventListener('click', (e) => {
        e.preventDefault()
        let div = document.getElementById('labelNoteDiv')
        div.classList.replace('show', 'hide')
    })    
}

// Show more content: Project Overview Page
function showMore(elem) {
    let idToMatch = elem.id
    let expandDiv = document.getElementById(`expand-div-${idToMatch}`)
    let contentCard = document.getElementById(`full-div-card-${idToMatch}`)

   expandDiv.classList.toggle('hide')
   expandDiv.classList.toggle('show')

    if (expandDiv.classList.contains('show')) {
        elem.innerHTML = 'Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>'
        if (contentCard) { contentCard.style.height = "auto" }
    } else {
        elem.innerHTML = 'Show More <i class="fa fa-angle-down" aria-hidden="true"></i>'
        if (contentCard) { contentCard.style.height = "auto" }
    }
}

// Community: create project
// Community: apply labels
function displayDefaultText(elem) {
    let isChecked = elem.checked
    let labelID = elem.id
    let targetNum = labelID.slice(14)

    let targetDiv = document.getElementById(`open-default-text-${targetNum}`)
    let labelName = document.getElementById(`label-name-${targetNum}`)

    if (isChecked) {
        targetDiv.style.height = 'auto'
        labelName.classList.replace('grey-text', 'darkteal-text')
    } else {
        targetDiv.style.height = '0'
        labelName.classList.replace('darkteal-text', 'grey-text')
    }

}


// TK Labels : community -> labels -> select labels
function showTKLabelInfo() {
    let labelContainer = document.getElementById('expand-tklabels')
    let span = document.getElementById('show-more-tk-down')
    let fullCard = document.getElementById('collapsed-tkcard')
    let header = document.getElementById('tklabels-title-vertical')

    if (labelContainer.style.height == "0px") {
        header.style.margin = "0"
        fullCard.style.height = "auto"
        labelContainer.style.height = "auto"
        span.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    } else {
        header.style.margin = "auto 0"
        fullCard.style.height = "113px"
        labelContainer.style.height = "0px"
        span.innerHTML = `Show More <i class="fa fa-angle-down" aria-hidden="true"></i>`
    }
}

// Select Label - View Info about label 
function expandTKLabel(img) {
    // Change Text Color on selected Label
    let txtDivs = Array.from(document.querySelectorAll('.toggle-txt-color'))
    txtDivs.forEach(node => {
        if (node == img.parentElement.nextElementSibling) { node.classList.replace('grey-text', 'darkteal-text') } else { node.classList.replace('darkteal-text', 'grey-text') }
    })

    const targetImg = img.id

    // Provanance
    let infoProv = document.getElementById('tklabel-info-prov')
    let titleProv = document.getElementById('tk-label-title-prov')
    let templateTextProv = document.getElementById('label-template-text-tk-prov')
    let whyUseLabelTextProv = document.getElementById('why-use-this-label-tk-prov')

    // Protocols
    let infoProt = document.getElementById('tklabel-info-prot')
    let titleProt = document.getElementById('tk-label-title-prot')
    let templateTextProt = document.getElementById('label-template-text-tk-prot')
    let whyUseLabelTextProt = document.getElementById('why-use-this-label-tk-prot')

    // Permissions
    let infoPerms = document.getElementById('tklabel-info-perm')
    let titlePerms = document.getElementById('tk-label-title-perm')
    let templateTextPerms = document.getElementById('label-template-text-tk-perm')
    let whyUseLabelTextPerms = document.getElementById('why-use-this-label-tk-perm')

    // Hidden inputs to store Label selected value
    let inputProv = document.getElementById('tk-label-value-type-prov')
    let inputProt = document.getElementById('tk-label-value-type-prot')
    let inputPerms = document.getElementById('tk-label-value-type-perm')

    fetchLabels('tk').then(populateTKLabel)

    function populateTKLabel(data) {
        data.forEach(tklabel => {
            if (tklabel.labelCode == targetImg) {
                displayExpandedImage(targetImg)
                checkLabelExists(tklabel, targetImg, 'TK')

                if (tklabel.labelCategory == 'protocol') {
                    openLabelInfoDiv(infoProt, infoProv, infoPerms)
                    //  Assign input value based on which tk label image is selected
                    inputProt.value = targetImg
                    titleProt.textContent = tklabel.labelName
                    templateTextProt.textContent = tklabel.labelDefaultText
                    whyUseLabelTextProt.textContent = tklabel.whyUseThisLabel       

                } else if (tklabel.labelCategory == 'provenance') {
                    openLabelInfoDiv(infoProv, infoProt, infoPerms)
                    inputProv.value = targetImg
                    titleProv.textContent = tklabel.labelName
                    templateTextProv.textContent = tklabel.labelDefaultText
                    whyUseLabelTextProv.textContent = tklabel.whyUseThisLabel

                } else if (tklabel.labelCategory == 'permission') {
                    openLabelInfoDiv(infoPerms, infoProt, infoProv)
                    inputPerms.value = targetImg
                    titlePerms.textContent = tklabel.labelName
                    templateTextPerms.textContent = tklabel.labelDefaultText
                    whyUseLabelTextPerms.textContent = tklabel.whyUseThisLabel       
                }
            }
        })
    }
}

// When Label is clicked to be customized, show details
function openLabelInfoDiv(targetDiv, divToCloseOne, divToCloseTwo) {
    // Open target div 
    if (targetDiv.classList.contains('hide')) { targetDiv.classList.replace('hide', 'show') }

    // Close other two divs if open
    if (divToCloseOne.classList.contains('show')) { divToCloseOne.classList.replace('show', 'hide') }
    if (divToCloseTwo.classList.contains('show')) { divToCloseTwo.classList.replace('show', 'hide') }
}

function closeLabelInfoDiv(targetBtn) {
    // Divs to close
    let infoTKProv = document.getElementById('tklabel-info-prov')
    let infoTKProt = document.getElementById('tklabel-info-prot')
    let infoTKPerm = document.getElementById('tklabel-info-perm')
    let infoBCProv = document.getElementById('bclabel-info-prov')
    let infoBCProt = document.getElementById('bclabel-info-prot')
    let infoBCPerm = document.getElementById('bclabel-info-perm')

    let btnId = targetBtn.id

    // Check if target button includes str in id
    let tkProv = btnId.includes('tk-prov')
    let bcProv = btnId.includes('bc-prov')
    let tkProt = btnId.includes('tk-prot')
    let bcProt = btnId.includes('bc-prot')
    let tkPerm = btnId.includes('tk-perm')
    let bcPerm = btnId.includes('bc-perm')

    switch(true) {
        case tkProv:
            infoTKProv.classList.replace('show', 'hide')        
            break;
        case bcProv:
            infoBCProv.classList.replace('show', 'hide')        
            break;
        case tkProt:
            infoTKProt.classList.replace('show', 'hide')
            break;
        case bcProt:
            infoBCProt.classList.replace('show', 'hide')
            break;
        case tkPerm:
            infoTKPerm.classList.replace('show', 'hide')
            break;
        case bcPerm:
            infoBCPerm.classList.replace('show', 'hide')
            break;
    }
}

// Institutions: create-projects : show notice descriptions
function showDescription() {
    let bcInput = document.getElementById('bc-notice')
    let tkInput = document.getElementById('tk-notice')
    let tkDescriptionDiv = document.getElementById('show-notice-description-tk')
    let bcDescriptionDiv = document.getElementById('show-notice-description-bc')
    let tkTarget = document.getElementById('tkTitle')
    let bcTarget = document.getElementById('bcTitle')

    if (bcInput.checked && tkInput.checked) {
        tkTarget.classList.replace('grey-text', 'darkteal-text')
        bcTarget.classList.replace('grey-text', 'darkteal-text')
        tkDescriptionDiv.style.display = "block"
        bcDescriptionDiv.style.display = "block"
    } else if (bcInput.checked) {
        tkTarget.classList.add('grey-text')
        bcTarget.classList.replace('grey-text', 'darkteal-text')
        bcDescriptionDiv.style.display = "block"
        tkDescriptionDiv.style.display = "none"
    } else if (tkInput.checked) {
        bcTarget.classList.add('grey-text')
        tkTarget.classList.replace('grey-text', 'darkteal-text')
        bcDescriptionDiv.style.display = "none"
        tkDescriptionDiv.style.display = "block"
    } else {
        tkTarget.classList.add('grey-text')
        bcTarget.classList.add('grey-text')
        bcDescriptionDiv.style.display = "none"
        tkDescriptionDiv.style.display = "none" 
    }

}

// CREATE PROJECT: PROJECT TYPE OTHER: TOGGLE VISIBILITY
var projectTypeSelect = document.getElementById('id_project_type')
if (projectTypeSelect) {
    projectTypeSelect.addEventListener('change', function() {
        let otherTypeField = document.getElementById('otherTypeField')
        if (projectTypeSelect.value == 'Other') {
            otherTypeField.classList.replace('hide', 'show')
        } else {
            otherTypeField.classList.replace('show', 'hide')
        }
    })
}

// Institutions: projects: notify communities - select desired communities
function selectCommunities() {
    let select = document.getElementById('communities-select')
    let allOptionsArray = Array.from(select.options)
    // Remove first element of options array
    let allOptionsMinusFirst = allOptionsArray.slice(1)

    allOptionsMinusFirst.forEach(option => {
        let selectedCommunityDiv = document.getElementById(`selected-community-${option.id}`)
        let div = document.getElementById(`comm-id-input-${option.id}`)

        if (option.selected) {
            // console.log(option)
            selectedCommunityDiv.style.height = "auto";
            div.innerHTML = `<input type="hidden" value="${option.id}" name="selected_communities">`
        }
    })
}

// INSTITUTION: create project : add contributors
function selectContributors() {
    let contribInput = document.getElementById('contributor-input')
    let contribOptionsArray = Array.from(document.getElementById('contributors').options)

    contribOptionsArray.forEach(option => {
        // compare input value to option value
        if (option.value == contribInput.value) {

            // push id to researcherArray or institutionArray
            if (contribInput.value.includes('Researcher')) {
                contribInput.value = ''

                let selectedResearcherDiv = document.getElementById(`selected-researcher-${option.dataset.resid}`)
                let div = document.getElementById(`res-id-input-${option.dataset.resid}`)
        
                selectedResearcherDiv.style.height = "auto"
                div.innerHTML = `<input type="hidden" value="${option.dataset.resid}" name="selected_researchers">`
            } else {
                contribInput.value = ''

                let selectedInstitutionDiv = document.getElementById(`selected-institution-${option.dataset.instid}`)
                let div = document.getElementById(`inst-id-input-${option.dataset.instid}`)

                selectedInstitutionDiv.style.height = "auto"
                div.innerHTML = `<input type="hidden" value="${option.dataset.instid}" name="selected_institutions">`
            }
        }
    })

}

var addContributorBtn = document.getElementById('add-contributor-btn')
if(addContributorBtn) {
    addContributorBtn.addEventListener('click', selectContributors)
}

function cancelInstitutionSelection(elem) {
    let id = elem.id
    let matches = id.match(/(\d+)/)
    let targetNum = matches[0]

    let divToClose = document.getElementById(`selected-institution-${targetNum}`)
    let inputDivToRemove = document.getElementById(`inst-id-input-${targetNum}`)

    divToClose.style.height = '0'
    inputDivToRemove.innerHTML = ``
}

function cancelResearcherSelection(elem) {
    let id = elem.id
    let matches = id.match(/(\d+)/)
    let targetNum = matches[0]
    console.log(targetNum)

    let divToClose = document.getElementById(`selected-researcher-${targetNum}`)
    let inputDivToRemove = document.getElementById(`res-id-input-${targetNum}`)

    divToClose.style.height = '0'
    inputDivToRemove.innerHTML = ``
}

// Add project people on institution create-project
// h/t: https://medium.com/all-about-django/adding-forms-dynamically-to-a-django-formset-375f1090c2b0
var count = 0

function cloneForm(el) {
    // In CREATE PROJECT:
    if (window.location.href.includes('/projects/create-project')) {
        // Total forms hidden input needs to be incremented
        let hiddenInputs = document.getElementsByName('form-TOTAL_FORMS')
        let totalFormInput = hiddenInputs[0]

        // Need to increment that number by 1 each time parent div is duplicated
        // Get parent div, clone it and change its attributes
        let parentDiv = document.getElementById('person-form-0')
        let clone = parentDiv.cloneNode(true)
        clone.id = 'person-form-'+ count++ // needs to increment by 1 for unique id

        // Name input has name='form-0-name' and id='id_form-0-name'
        // Email input has name='form-0-email' and id='id_form-0-email'

        let nameInput = clone.getElementsByTagName('input')[0]
        let emailInput = clone.getElementsByTagName('input')[1]
        nameInput.value = ''
        emailInput.value = ''
        nameInput.id = `id_form-${count}-name`
        nameInput.name = `form-${count}-name`
        emailInput.id = `id_form-${count}-email`
        emailInput.name = `form-${count}-email`
        totalFormInput.value = parseInt(totalFormInput.value) + 1

        // Append clone to sibling
        el.parentElement.parentElement.append(clone)

        // IN EDIT PROJECT:
    } else if (window.location.href.includes('/projects/edit-project')) {
        // Total forms hidden input needs to be incremented
        let hiddenInputs = document.getElementsByName('additional_contributors-TOTAL_FORMS')
        let totalFormInput = hiddenInputs[0]

        // Need to increment that number by 1 each time parent div is duplicated
        // Get parent div, clone it and change its attributes
        let parentDiv = document.getElementById('person-form-0')
        let clone = parentDiv.cloneNode(true)
        clone.id = 'person-form-'+ count++ // needs to increment by 1 for unique id

        // Name input has name='additional_contributors-0-name' and id='id_additional_contributors-0-name'
        // Email input has name='additional_contributors-0-email' and id='id_additional_contributors-0-email'

        let nameInput = clone.getElementsByTagName('input')[0]
        let emailInput = clone.getElementsByTagName('input')[1]
        nameInput.value = ''
        emailInput.value = ''
        nameInput.id = `id_additional_contributors-${count}-name`
        nameInput.name = `additional_contributors-${count}-name`
        emailInput.id = `id_additional_contributors-${count}-email`
        emailInput.name = `additional_contributors-${count}-email`
        totalFormInput.value = parseInt(totalFormInput.value) + 1

        // Append clone to sibling
        el.parentElement.parentElement.append(clone)
    }

}

// Institutions: projects: notify communities - close selected communities
function cancelCommunitySelection(elem) {
    let id = elem.id
    let matches = id.match(/(\d+)/)
    let targetNum = matches[0]

    let divToClose = document.getElementById(`selected-community-${targetNum}`)
    let inputDivToRemove = document.getElementById(`comm-id-input-${targetNum}`)

    divToClose.style.height = '0'
    inputDivToRemove.innerHTML = ``
}

// Communities: Projects: Notify status
function setProjectUUID(elem) {
    let elementId = elem.id
    let projectID = elementId.slice(7)
    let statusSelect = document.getElementById(elementId)
    let projectIdInput = document.getElementById(`project-id-input-${projectID}`)
    let statusSelectedInput = document.getElementById(`status-selection-input-${projectID}`)

    // Set first hidden value to project UUID
    projectIdInput.value = projectID
    // Set second hidden value to value of option selected
    statusSelectedInput.value = statusSelect.options[statusSelect.selectedIndex].value
}

// Require Checkbox selection for Notices in create-project researcher and institution
// h/t: https://vyspiansky.github.io/2019/07/13/javascript-at-least-one-checkbox-must-be-selected/

if (window.location.href.includes('researcher/projects/create-project') || window.location.href.includes('institution/projects/create-project') ) { 
    (function requireCheckbox() {
        let form = document.querySelector('#createProjectForm')
        let checkboxes = form.querySelectorAll('input[type=checkbox]')
        let checkboxLength = checkboxes.length
        let firstCheckbox = checkboxLength > 0 ? checkboxes[0] : null
    
        function start() {
            if (firstCheckbox) {
                for (let i = 0; i < checkboxLength; i++) {
                    checkboxes[i].addEventListener('change', checkValidity)
                }
                checkValidity()
            }
        }
    
        function isChecked() {
            for (let i = 0; i < checkboxLength; i++) {
                if (checkboxes[i].checked) return true
            }
            return false
        }
    
        function checkValidity() {
            const errorMsg = !isChecked() ? 'At least one Notice must be selected.' : ''
            firstCheckbox.setCustomValidity(errorMsg)
        }
    
        start()
    })()
}

// Project Overview meatball menu
function toggleMeatballMenu(elem) {
    let slicedID = elem.id.slice(9)
    document.getElementById(`meatball-content-${slicedID}`).classList.toggle('hide')
    document.getElementById(`meatball-content-${slicedID}`).classList.toggle('show')
}

function toggleNotifications() {
    document.getElementById('notification-v2').classList.toggle('show')

    window.onclick = function(event) {
        if(!event.target.matches('.dropbtn')) {
            let dropdowns = document.getElementsByClassName("notification-dropdown-content")
            for (let i=0; i < dropdowns.length; i++) {
                let openDropdown = dropdowns[i]
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show')
                }
            }
        }
    }
}

function showUserNotifications(btn) {
    let div = document.getElementById('userNotifications')
    div.classList.toggle('hide')
    if (div.classList.contains('hide')) { btn.classList.replace('white-btn', 'action-btn') } else { btn.classList.replace( 'action-btn', 'white-btn') }
}


if (window.location.href.includes('connect-community') || window.location.href.includes('connect-institution')) {

    let inputList = document.getElementById('selectedOrganizationInputList')
    inputList.addEventListener('change', setCommunity)
    inputList.addEventListener('click', setCommunity)

    function setCommunity() {
        let hiddenCommunityInput = document.getElementById('hidden-target-input')
        hiddenCommunityInput.value = inputList.value
    }

    // Join an organization
    const joinBtn = document.getElementById('openJoinRequestModalBtn')
    joinBtn.addEventListener('click', function(e) {

        // handle when inputlist value is ''
        if (!inputList.value) {
            alert('Please select an organization from the list')
        } else {
            e.preventDefault()
            let modal = document.getElementById('joinRequestModal')
            if (modal.classList.contains('hide')) {
                modal.classList.replace('hide', 'show')
            }
        
            let span = document.querySelector('.close-modal')
            span.onclick = function() {
                modal.classList.replace('show', 'hide')
            }
        }
    })
}   

// Copy text to clipboard
function copyToClipboard() {
    let span = document.getElementById('uniqueIDToCopy')
    var textArea = document.createElement("textarea");
    textArea.value = span.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("Copy");
    textArea.remove();
}

// Connect-researcher: ORCiD popup
if (window.location.href.includes('connect-researcher')) {
    const createResearcherBtn = document.getElementById('submitResearcher')

    createResearcherBtn.addEventListener('click', function(event) {
        event.preventDefault()
        let hiddenORCIDInput = document.getElementById('orcidId')
    
        //If it isn't "undefined" and it isn't "null", then it exists.
        if(typeof(hiddenORCIDInput) != 'undefined' && hiddenORCIDInput != null){
            document.getElementById('createResearcher').submit()
        } else {
            // Show modal
            let modal = document.getElementById('ORCIDmodal')
            modal.classList.replace('hide', 'show')

            // Close modal
            let closeBtn = document.getElementById('closeORCIDmodal')
            closeBtn.addEventListener('click', function(event) { modal.classList.replace('show', 'hide') })

            // Continue without orcid
            let continueBtn = document.getElementById('continueNoOrcidBtn')
            continueBtn.addEventListener('click', function(event) { document.getElementById('createResearcher').submit() })
        }
    })  
}

if (window.location.href.includes('registry')) {
    const registryModal = document.getElementById('registryModal')
    const submitJoinRequestFormBtn = document.getElementById('submitRegistryForm')

    const closeRegistryModalBtn = document.getElementById('closeRegistryModal')
    closeRegistryModalBtn.addEventListener('click', function(e) { registryModal.classList.replace('show', 'hide') })

    document.addEventListener('click', function(e) {

        if (e.target.tagName == 'BUTTON') {
            e.preventDefault()
            // show modal
            registryModal.classList.replace('hide', 'show')

            // get Id and btn type, based on which organization it is, submit
            if (e.target.id.includes('community')) {
                let targetId = e.target.id.split('-').pop()
                submitJoinRequestFormBtn.addEventListener('click', function(e) { document.getElementById(`communityRegistryForm${targetId}`).submit() })    
            } else if (e.target.id.includes('institution')) {
                let targetId = e.target.id.split('-').pop()
                submitJoinRequestFormBtn.addEventListener('click', function(e) { document.getElementById(`institutionRegistryForm${targetId}`).submit() })    
            }
        }
    })       
}

function openMemberModal() {
    const memberModal = document.getElementById('memberModal')
    memberModal.classList.replace('hide', 'show')

    const closeBtn = document.querySelector('.close-modal-btn')
    closeBtn.onclick = function() {
        memberModal.classList.replace('show', 'hide')
    }
}

// Deactivate user popup in user settings
var deactivateAccountBtn = document.getElementById('submitDeactivation')
if (deactivateAccountBtn) {
    deactivateAccountBtn.addEventListener('click', function(event) {
        event.preventDefault()
        let deactivationModal = document.getElementById('deactivationModal')
        deactivationModal.classList.replace('hide', 'show')

        let cancelBtn = document.getElementById('closeDeactivationModal')
        cancelBtn.addEventListener('click', function(event) { deactivationModal.classList.replace('show', 'hide')})

        let continueDeactivationBtn = document.getElementById('continueDeactivationBtn')
        continueDeactivationBtn.addEventListener('click', function(){ document.getElementById('deactivateUserForm').submit() })
    })
}

// REGISTRY FILTERING
if (window.location.href.includes('registry')) {
    // Filter Registry
    const filterbyCommunities = document.getElementById('filterCommunities')
    const filterbyInstitutions = document.getElementById('filterInstitutions')
    const filterbyAll = document.getElementById('filterAll')
    let institutions = document.querySelectorAll('.institutions-filter')
    let communities = document.querySelectorAll('.communities-filter')

    filterbyCommunities.addEventListener('click', () => {
        institutions.forEach(institution => { institution.classList.replace('show', 'hide') })
        communities.forEach(community => { if (community.classList.contains('hide')) { community.classList.replace('hide', 'show') } })
    })

    filterbyInstitutions.addEventListener('click', () => { 
        communities.forEach(community => { community.classList.replace('show', 'hide') })
        institutions.forEach(institution => { if (institution.classList.contains('hide')) { institution.classList.replace('hide', 'show') } })
    })
    
    filterbyAll.addEventListener('click', () => {
        communities.forEach(community => { if (community.classList.contains('hide')) { community.classList.replace('hide', 'show') } })
        institutions.forEach(institution => { if (institution.classList.contains('hide')) { institution.classList.replace('hide', 'show') } })
    })
}

//  ONBOARDING MODAL: Shows up in dashboard if user does not have a last_login & there isn't a localstorage item saved
if (window.location.href.includes('dashboard')) {
    const hiddenInput = document.getElementById('openOnboarding')
    const onboardingModal = document.getElementById('onboardingModal')
    const closeOnboardBtns = document.querySelectorAll('.close-onboarding-btn')
    const nextBtns = document.querySelectorAll('.btn-next')
    const modalSteps = document.querySelectorAll('.onboard-step')

    let modalStepsNum = 0
    // If user does not have a last login and nothing is stored on localstorage
    if (hiddenInput.value == 'true' && !localStorage.getItem('closedOnboarding')) {
        // show modal
        onboardingModal.classList.replace('hide', 'show')
    } else {
        // if modal is showing, hide it
        if (onboardingModal.classList.contains('show')) {
            onboardingModal.classList.replace('show', 'hide')
        } else {
            onboardingModal.classList.add('hide')
        }
    }
    
    closeOnboardBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            onboardingModal.classList.add('hide')
            localStorage.setItem('closedOnboarding', 'true')
        })
    })
   
    nextBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            modalStepsNum++
            updateModalSteps()
        })
    })

    function updateModalSteps() {
        modalSteps.forEach(modalStep => {
            modalStep.classList.contains('onboard-step-active') &&
            modalStep.classList.remove('onboard-step-active')
        })
        modalSteps[modalStepsNum].classList.add('onboard-step-active')
    }
}

