// Dismiss Messages
var dismissBtn = document.getElementById('close-btn')
var messageDiv = document.getElementById('alert-message')

if (dismissBtn) { dismissBtn.addEventListener('click', () => { messageDiv.style.display = 'none'}) }

// Password fields in registration form
var passwordField = document.getElementById('id_password1')
var helpTextDiv = document.getElementById('help-text-pw')

if (passwordField ) {
    passwordField.addEventListener('focusin', (event) => { helpTextDiv.style.display = 'block' })
    passwordField.addEventListener('focusout', (event) => { helpTextDiv.style.display = 'none' })
}

// Show customized label text in community: labels
function customText(imgDiv) {
    let labelID = imgDiv.id
    let divs = Array.from(document.querySelectorAll('.div-toggle'))
    // console.log(labelID)

    divs.forEach(div => {
        if (div.id.includes(labelID) && div.style.height == '0px') {
            // console.log(div.id)
            div.style.height = 'auto'
        } else {
            div.style.height = '0px'
        }
    })


    // Toggle text color based on what Label is selected
    let pDivs = Array.from(document.querySelectorAll('.toggle-txt-color'))
    pDivs.forEach(node => {
        let nodeID = node.id
        if (nodeID.includes(labelID)) {
            node.classList.add('darkteal-text')
            node.classList.remove('grey-text')
        } else {
            node.classList.remove('darkteal-text')
            node.classList.add('grey-text')
        }
    })
}

async function fetchLabels(type) {
    const response = await fetch('/static/json/Labels.json')
    const data = await response.json()
    if (type == 'bc') {
        return data.bcLabels
    } else if (type == 'tk') {
        return data.tkLabels
    } else if (type == 'both') {
        return data
    }
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
    txtDivs.forEach(node => {
        if (node == img.parentElement.nextElementSibling) {
            node.classList.remove('grey-text')
            node.classList.add('darkteal-text')
 
        } else {
            node.classList.remove('darkteal-text')
            node.classList.add('grey-text')
        }
    })

    let fullCard = document.getElementById('collapsed-card')
    let labelContainer = document.getElementById('expand-bclabels')
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

    function openBCInfoDiv(targetDiv) {
        if (targetDiv.style.height == "0px") {
            labelContainer.style.height = "auto"
            targetDiv.style.height = "auto"
            fullCard.style.height = "auto"
        } else {
            labelContainer.style.height = "auto"
            targetDiv.style.height = "0px"
            fullCard.style.height = "auto"
        }       
    }

    fetchLabels('bc').then(populateBCLabel)

    // Set content based on which Label was selected
    function populateBCLabel(data) {
        data.forEach(bclabel => {
            if (bclabel.labelCode == targetImg) { 
                displayExpandedImage(targetImg)
                checkBCLabelExists(bclabel, targetImg)

                if (bclabel.labelCategory == 'protocol') {
                    openBCInfoDiv(infoProt)
                    //  Assign input value based on which bc label image is selected
                    inputProt.value = targetImg
                    titleProt.textContent = bclabel.labelName
                    templateTextProt.textContent = bclabel.labelDefaultText
                    whyUseLabelTextProt.textContent = bclabel.whyUseThisLabel  
                
                } else if (bclabel.labelCategory == 'provenance') {
                    openBCInfoDiv(infoProv)
                    inputProv.value = targetImg
                    titleProv.textContent = bclabel.labelName
                    templateTextProv.textContent = bclabel.labelDefaultText
                    whyUseLabelTextProv.textContent = bclabel.whyUseThisLabel

                } else if (bclabel.labelCategory == 'permission') {
                    openBCInfoDiv(infoPerms)
                    inputPerms.value = targetImg
                    titlePerms.textContent = bclabel.labelName
                    templateTextPerms.textContent = bclabel.labelDefaultText
                    whyUseLabelTextPerms.textContent = bclabel.whyUseThisLabel
                }
            }
        })
    }

    function checkBCLabelExists(label, targetLabelCode) {
        let btnBCProv = document.getElementById('btnBCProv')
        let btnBCProt = document.getElementById('btnBCProt')
        let btnBCPerms = document.getElementById('btnBCPerms')

        // Takes all hidden inputs with the label_type of labels that have already been created by the community
        let inputs = Array.from(document.querySelectorAll('.checkBCLabelType'))
        inputs.forEach(input => {
            if (label.labelCode == targetLabelCode) {
                if (input.value == label.labelType) {
                    // get label category, then get the button for that section
                    // disable the btn
                    if (label.labelCategory == 'provenance') {
                        btnBCProv.disabled = true
                        btnBCProv.classList.remove('action-btn')
                        btnBCProv.classList.add('disabled-btn')
                    } else if (label.labelCategory == 'protocol') {
                        btnBCProt.disabled = true
                        btnBCProt.classList.remove('action-btn')
                        btnBCProt.classList.add('disabled-btn')
                    } else if (label.labelCategory == 'permission') {
                        btnBCPerms.disabled = true
                        btnBCPerms.classList.remove('action-btn')
                        btnBCPerms.classList.add('disabled-btn')
                    }
                } else {
                    if (label.labelCategory == 'provenance') {
                        btnBCProv.disabled = false
                        btnBCProv.classList.remove('disabled-btn')
                        btnBCProv.classList.add('action-btn')
                    } else if (label.labelCategory == 'protocol') {
                        btnBCProt.disabled = false
                        btnBCProt.classList.remove('disabled-btn')
                        btnBCProt.classList.add('action-btn')
                    } else if (label.labelCategory == 'permission') {
                        btnBCPerms.disabled = false
                        btnBCPerms.classList.remove('disabled-btn')
                        btnBCPerms.classList.add('action-btn')
                    }
                }
            } 
        })
    }

}

// Display Label images that was clicked in the expanded Div
function displayExpandedImage(type) {
    let imgArray

    if (type.startsWith('b')) {
        imgArray = Array.from(document.querySelectorAll('.bc-img-div'))
    } else if (type.startsWith('t')) {
        imgArray = Array.from(document.querySelectorAll('.tk-img-div'))
    }

    for (let i = 0; i < imgArray.length; i ++) {
        // take the id and split it, compare type to the split
        if (imgArray[i].id.slice(21) == type) {
            imgArray[i].style.display = 'block'
        } else {
            imgArray[i].style.display = 'none'
        }
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

// Show more content: Project Overview Page
function showMore(elem) {
    let idToMatch = elem.id
    let expandDiv = document.getElementById(`expand-div-${idToMatch}`)
    let contentCard = document.getElementById(`full-div-card-${idToMatch}`)

   expandDiv.classList.toggle('hide')
   expandDiv.classList.toggle('show')

    if (expandDiv.classList.contains('show')) {
        elem.innerHTML = 'Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>'
        contentCard.style.height = "auto"
    } else {
        elem.innerHTML = 'Show More <i class="fa fa-angle-down" aria-hidden="true"></i>'
        contentCard.style.height = "auto"
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
        labelName.classList.remove('grey-text')
        labelName.classList.add('darkteal-text')
    } else {
        targetDiv.style.height = '0'
        labelName.classList.remove('darkteal-text')
        labelName.classList.add('grey-text')
    }

}


// TK Labels : community -> customize -> select labels
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
        if (node == img.parentElement.nextElementSibling) {
            node.classList.remove('grey-text')
            node.classList.add('darkteal-text')
        } else {
            node.classList.remove('darkteal-text')
            node.classList.add('grey-text')
        }
    })

    let labelContainer = document.getElementById('expand-tklabels')
    let fullCard = document.getElementById('collapsed-tkcard')
    let targetImg = img.id

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
    let infoPerms = document.getElementById('tklabel-info-perms')
    let titlePerms = document.getElementById('tk-label-title-perms')
    let templateTextPerms = document.getElementById('label-template-text-tk-perms')
    let whyUseLabelTextPerms = document.getElementById('why-use-this-label-tk-perms')

    let inputProv = document.getElementById('tk-label-value-type-prov')
    let inputProt = document.getElementById('tk-label-value-type-prot')
    let inputPerms = document.getElementById('tk-label-value-type-perms')

    function openInfoDiv(targetDiv) {
        if (targetDiv.style.height == "0px") {
            labelContainer.style.height = "auto"
            targetDiv.style.height = "auto"
            fullCard.style.height = "auto"
        } else {
            labelContainer.style.height = "auto"
            targetDiv.style.height = "0px"
            fullCard.style.height = "auto"
        }
    }

    fetchLabels('tk').then(populateTKLabel)

    function populateTKLabel(data) {
        data.forEach(tklabel => {
            if (tklabel.labelCode == targetImg) {
                displayExpandedImage(targetImg)
                checkTKLabelExists(tklabel, targetImg)

                if (tklabel.labelCategory == 'protocol') {
                    openInfoDiv(infoProt)
                    //  Assign input value based on which tk label image is selected
                    inputProt.value = targetImg
                    titleProt.textContent = tklabel.labelName
                    templateTextProt.textContent = tklabel.labelDefaultText
                    whyUseLabelTextProt.textContent = tklabel.whyUseThisLabel       

                } else if (tklabel.labelCategory == 'provenance') {
                    openInfoDiv(infoProv)
                    inputProv.value = targetImg
                    titleProv.textContent = tklabel.labelName
                    templateTextProv.textContent = tklabel.labelDefaultText
                    whyUseLabelTextProv.textContent = tklabel.whyUseThisLabel

                } else if (tklabel.labelCategory == 'permission') {
                    openInfoDiv(infoPerms)
                    inputPerms.value = targetImg
                    titlePerms.textContent = tklabel.labelName
                    templateTextPerms.textContent = tklabel.labelDefaultText
                    whyUseLabelTextPerms.textContent = tklabel.whyUseThisLabel       
                }
            }
        })
    }

    function checkTKLabelExists(label, targetLabelCode) {
        let btnTKProv = document.getElementById('btnTKProv')
        let btnTKProt = document.getElementById('btnTKProt')
        let btnTKPerms = document.getElementById('btnTKPerms')

        // Takes all hidden inputs with the label_type of labels that have already been created by the community
        let inputs = Array.from(document.querySelectorAll('.checkTKLabelType'))
        inputs.forEach(input => {
            if (label.labelCode == targetLabelCode) {
                if (input.value == label.labelType) {
                    // get label category, then get the button for that section
                    // disable the btn
                    if (label.labelCategory == 'provenance') {
                        btnTKProv.disabled = true
                        btnTKProv.classList.remove('action-btn')
                        btnTKProv.classList.add('disabled-btn')
                    } else if (label.labelCategory == 'protocol') {
                        btnTKProt.disabled = true
                        btnTKProt.classList.remove('action-btn')
                        btnTKProt.classList.add('disabled-btn')
                    } else if (label.labelCategory == 'permission') {
                        btnTKPerms.disabled = true
                        btnTKPerms.classList.remove('action-btn')
                        btnTKPerms.classList.add('disabled-btn')
                    }
                } else {
                    if (label.labelCategory == 'provenance') {
                        btnTKProv.disabled = false
                        btnTKProv.classList.remove('disabled-btn')
                        btnTKProv.classList.add('action-btn')
                    } else if (label.labelCategory == 'protocol') {
                        btnTKProt.disabled = false
                        btnTKProt.classList.remove('disabled-btn')
                        btnTKProt.classList.add('action-btn')
                    } else if (label.labelCategory == 'permission') {
                        btnTKPerms.disabled = false
                        btnTKPerms.classList.remove('disabled-btn')
                        btnTKPerms.classList.add('action-btn')
                    }
                }
            } 
        })
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
        tkTarget.classList.add('darkteal-text')
        tkTarget.classList.remove('grey-text')
        bcTarget.classList.add('darkteal-text')
        bcTarget.classList.remove('grey-text')
        tkDescriptionDiv.style.display = "block"
        bcDescriptionDiv.style.display = "block"
    } else if (bcInput.checked) {
        tkTarget.classList.add('grey-text')
        bcTarget.classList.add('darkteal-text')
        bcTarget.classList.remove('grey-text')
        bcDescriptionDiv.style.display = "block"
        tkDescriptionDiv.style.display = "none"
    } else if (tkInput.checked) {
        bcTarget.classList.add('grey-text')
        tkTarget.classList.add('darkteal-text')
        tkTarget.classList.remove('grey-text')
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
            otherTypeField.style.display = 'block'
        } else {
            otherTypeField.style.display = 'none'
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

    if (div.classList.contains('hide')) {
        btn.classList.remove('active-dash-driver-btn')
        btn.classList.add('action-btn')
    } else {
        btn.classList.add('active-dash-driver-btn')
        btn.classList.remove('action-btn')    
    }

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
    let nameToCheckInput = document.querySelector('.nameToCheck')

    joinBtn.addEventListener('click', function(e) {
        if (!inputList.value) {
            alert('Please select an organization from the list')
        } else if (nameToCheckInput.value != inputList.value) {
            alert('This organization is not yet registered in the Hub')
        } else {
            e.preventDefault()
            // handle when inputlist value is ''
            let modal = document.getElementById('joinRequestModal')
            if (modal.style.display == 'none') {
                modal.style.display = 'block'
            }
        
            let span = document.querySelector('.close-modal')
            span.onclick = function() {
                modal.style.display = "none";
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
            modal.style.display = 'block'

            // Close modal
            let closeBtn = document.getElementById('closeORCIDmodal')
            closeBtn.addEventListener('click', function(event) { modal.style.display = 'none' })

            // Continue without orcid
            let continueBtn = document.getElementById('continueNoOrcidBtn')
            continueBtn.addEventListener('click', function(event) { document.getElementById('createResearcher').submit() })
        }
    })  
}
  


// Deactivate user popup in user settings
var deactivateAccountBtn = document.getElementById('submitDeactivation')
if (deactivateAccountBtn) {
    deactivateAccountBtn.addEventListener('click', function(event) {
        event.preventDefault()
        let deactivationModal = document.getElementById('deactivationModal')
        deactivationModal.style.display = 'block'

        let cancelBtn = document.getElementById('closeDeactivationModal')
        cancelBtn.addEventListener('click', function(event) { deactivationModal.style.display = 'none' })

        let continueDeactivationBtn = document.getElementById('continueDeactivationBtn')
        continueDeactivationBtn.addEventListener('click', function(){ document.getElementById('deactivateUserForm').submit() })
    })
}

if (window.location.href.includes('registry')) {
    // Filter Registry
    const filterbyCommunities = document.getElementById('filterCommunities')
    const filterbyInstitutions = document.getElementById('filterInstitutions')
    const filterbyAll = document.getElementById('filterAll')
    let institutions = document.querySelectorAll('.institutions-filter')
    let communities = document.querySelectorAll('.communities-filter')


    filterbyCommunities.addEventListener('click', () => {
        institutions.forEach(institution => {
            institution.classList.remove('show')
            institution.classList.add('hide')
        })

        communities.forEach(community => {
            if (community.classList.contains('hide')) {
                community.classList.remove('hide')
                community.classList.add('show')
            }
        })
    })

    filterbyInstitutions.addEventListener('click', () => {
        communities.forEach(community => {
            community.classList.remove('show')
            community.classList.add('hide')

        })

        institutions.forEach(institution => {
            if (institution.classList.contains('hide')) {
                institution.classList.remove('hide')
                institution.classList.add('show')
            }
        })
    })
    
    filterbyAll.addEventListener('click', () => {
        communities.forEach(community => {
            if (community.classList.contains('hide')) {
                community.classList.remove('hide')
                community.classList.add('show')
            }
        })

        institutions.forEach(institution => {
            if (institution.classList.contains('hide')) {
                institution.classList.remove('hide')
                institution.classList.add('show')
            }
        })
    })
}

