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

// Get languages from the IANA directory
function fetchLanguages() {
    const endpoint = 'https://raw.githubusercontent.com/biocodellc/localcontexts_json/main/data/ianaObj.json'
    
    fetch(endpoint)
        .then(response => {
            if (response.ok) {
                return response.json()
            } else if (response.status === 404) {
                return Promise.reject('404 Not Found')
            }
        })
        .then(data => { languageList(data) })
        .catch((err) => {console.error('Error: ', err)})
}

function languageList(data) {
    let langArray = Object.keys(data)
    // feed only array of languages into this function
    autocomplete(document.getElementById('languageListInput'), langArray)
}

// Searchbar with autocomplete
// Takes two args: text iput element and array of values to autocomplete
function autocomplete(inp, arr) {
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);

        for (i = 0; i < arr.length; i++) {
          /*check if the item starts with the same letters as the text field value:*/
          if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");
            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
            b.innerHTML += arr[i].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                inp.setAttribute('value', this.getElementsByTagName("input")[0].value)
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            a.appendChild(b);
          }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
          /*If the arrow DOWN key is pressed,
          increase the currentFocus variable:*/
          currentFocus++;
          /*and and make the current item more visible:*/
          addActive(x);
        } else if (e.keyCode == 38) { //up
          /*If the arrow UP key is pressed,
          decrease the currentFocus variable:*/
          currentFocus--;
          /*and and make the current item more visible:*/
          addActive(x);
        } else if (e.keyCode == 13) {
          /*If the ENTER key is pressed, prevent the form from being submitted,*/
          e.preventDefault();
          if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (x) x[currentFocus].click();
          }
        }
    });

    function addActive(x) {
      /*a function to classify an item as "active":*/
      if (!x) return false;
      /*start by removing the "active" class on all items:*/
      removeActive(x);
      if (currentFocus >= x.length) currentFocus = 0;
      if (currentFocus < 0) currentFocus = (x.length - 1);
      /*add class "autocomplete-active":*/
      x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
      /*a function to remove the "active" class from all autocomplete items:*/
      for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
      }
    }

    function closeAllLists(elmnt) {
      /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
      var x = document.getElementsByClassName("autocomplete-items");
      for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }

  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
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
        if (nodeID.includes(labelID)) { node.classList.add('label-name-active') } else { node.classList.remove('label-name-active') }
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

// Customize Label: clone translation form to add multiple translations
if (window.location.href.includes('/labels/customize') || window.location.href.includes('/labels/edit')) {
    const addTranslationBtn = document.getElementById('add-translation-btn')
    if (addTranslationBtn) { addTranslationBtn.addEventListener('click', cloneForm, false)}

    // h/t: https://www.brennantymrak.com/articles/django-dynamic-formsets-javascript

    function cloneForm(e) {
        e.stopImmediatePropagation()
        e.preventDefault()
        
        let translationForm = document.querySelectorAll('.add-translation-form')
        let container = document.querySelector('#translation-form-container')
        let totalForms = document.querySelector("#id_form-TOTAL_FORMS")
        let lastDiv = document.getElementById('lastDiv')

        let formNum = translationForm.length-1

        let newForm = translationForm[0].cloneNode(true)
        let formRegex = RegExp(`form-(\\d){1}-`,'g')

        formNum++

        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`)
        container.insertBefore(newForm, lastDiv)
        totalForms.setAttribute('value', `${formNum+1}`)
    }

    fetchLanguages()
}

// Approve Label: show note div
if (window.location.href.includes('community/labels/')) {
    const noBtn = document.getElementById('displayLabelNote')
    const closeNoteDivBtn = document.getElementById('closeNoteDiv')

    if (noBtn && closeNoteDivBtn) {
        noBtn.addEventListener('click', (e) => {
            e.preventDefault()
            let div = document.getElementById('labelNoteDiv')
            div.classList.remove('hide')
            div.classList.add('show')
        })

        closeNoteDivBtn.addEventListener('click', (e) => {
            e.preventDefault()
            let div = document.getElementById('labelNoteDiv')
            div.classList.replace('show', 'hide')
        }) 
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

// Institutions/researchers: create-project: select Notices, show Notice descriptions
function showDescription() {
    let textinputs = document.querySelectorAll('input[type=checkbox]'); 
    // stores selected inputs in an array
    let selected = [].filter.call( textinputs, function( el ) {

        let target = document.getElementById(`show-description-${el.id}`)
        let pTag = document.getElementById(`title-${el.id}`)

        if (el.checked) {
            target.classList.replace('hide', 'show')
            pTag.classList.replace('grey-text', 'darkteal-text')
        } else {
            target.classList.replace('show', 'hide')
            pTag.classList.replace('darkteal-text', 'grey-text')
        }
    });
    // console.log('selected', selected)
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

// CREATE PROJECT: Disable submit temporarily
var submitProjectBtn = document.getElementById('submitProjectBtn')
if (submitProjectBtn) {
    submitProjectBtn.addEventListener('click', function(e) {
        let createProjectForm = document.getElementById('createProjectForm')
        createProjectForm.submit()

        let oldValue = 'Save Project'
        submitProjectBtn.setAttribute('disabled', true)
        submitProjectBtn.classList.replace('action-btn', 'disabled-btn')
        submitProjectBtn.innerText = 'Saving Project...'

        setTimeout(function(){
            submitProjectBtn.innerText = oldValue;
            submitProjectBtn.classList.replace('disabled-btn', 'action-btn')
            submitProjectBtn.removeAttribute('disabled');
        }, 4000)

    })
}

// PROJECTS: NOTIFY communities - select desired communities
function selectCommunities() {
    let select = document.getElementById('communities-select')
    let allOptionsArray = Array.from(select.options)
    // Remove first element of options array
    let allOptionsMinusFirst = allOptionsArray.slice(1)

    allOptionsMinusFirst.forEach(option => {
        let selectedCommunityDiv = document.getElementById(`selected-community-${option.id}`)
        let div = document.getElementById(`comm-id-input-${option.id}`)

        if (option.selected) {
            selectedCommunityDiv.classList.replace('hide', 'show')
            div.innerHTML = `<input type="hidden" value="${option.id}" name="selected_communities">`
        }
    })
}

// Projects: notify communities - close selected
function cancelCommunitySelection(elem) {
    let id = elem.id
    let matches = id.match(/(\d+)/)
    let targetNum = matches[0]

    let divToClose = document.getElementById(`selected-community-${targetNum}`)
    let inputDivToRemove = document.getElementById(`comm-id-input-${targetNum}`)

    divToClose.classList.replace('show', 'hide')
    inputDivToRemove.innerHTML = ``
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
        
                selectedResearcherDiv.classList.replace('hide', 'show')
                div.innerHTML = `<input type="hidden" value="${option.dataset.resid}" name="selected_researchers">`
            } else {
                contribInput.value = ''

                let selectedInstitutionDiv = document.getElementById(`selected-institution-${option.dataset.instid}`)
                let div = document.getElementById(`inst-id-input-${option.dataset.instid}`)

                selectedInstitutionDiv.classList.replace('hide', 'show')
                div.innerHTML = `<input type="hidden" value="${option.dataset.instid}" name="selected_institutions">`
            }
        }
    })
}

var addContributorBtn = document.getElementById('add-contributor-btn')
if(addContributorBtn) { addContributorBtn.addEventListener('click', selectContributors) }


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
            const modal = document.getElementById('joinRequestModal')
            if (modal.classList.contains('hide')) {
                modal.classList.replace('hide', 'show')
            }
        
            const closeModalBtn = document.querySelector('.close-modal-btn')
            closeModalBtn.addEventListener('click', function() {
                modal.classList.replace('show', 'hide')
            })
        }
    })
}   

// Copy text to clipboard
function copyToClipboard(elemID) {
    let span = document.getElementById(elemID)
    var textArea = document.createElement("textarea");
    textArea.value = span.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("Copy");
    textArea.remove();
}

// Add member modal
function openMemberModal() {
    const memberModal = document.getElementById('memberModal')
    memberModal.classList.replace('hide', 'show')

    const closeBtn = document.querySelector('.close-modal-btn')
    closeBtn.onclick = function() {
        memberModal.classList.replace('show', 'hide')
    }
}

function acceptJoinRequestModal(elem) {
    let modal = document.getElementById(`acceptJoinRequestModal_${elem.id}`)
    modal.classList.replace('hide', 'show')
    
    const closeBtn = document.getElementById(`closeModal${elem.id}`)
    closeBtn.onclick = function() {
        modal.classList.replace('show', 'hide')
    }
}

// use
// openBtnClasses: '.example'
// modalPartialId: 'modalName'
// closeBtnPartialId: 'closeModalBtn'
function modalToggle(openBtnClasses, modalPartialId, closeBtnPartialId) {
    const roleBtns = document.querySelectorAll(openBtnClasses)
    roleBtns.forEach(btn => {
        let buttonId = btn.id
        let arr = buttonId.split('_')
        let primary_id = arr[0]
        let user_id = arr[1]

        const openChangeRoleBtn = document.getElementById(`${primary_id}_${user_id}`)
        openChangeRoleBtn.addEventListener('click', function(e) {
            e.preventDefault()
            openTargetModal(user_id)
        })
    })

    function openTargetModal(id) {
        const modal = document.getElementById(`${modalPartialId}_${id}`)
        modal.classList.replace('hide', 'show')

        const closeModalBtn = document.getElementById(`${closeBtnPartialId}_${id}`)
        closeModalBtn.addEventListener('click', function(e) {
            e.preventDefault()
            modal.classList.replace('show', 'hide')
        })    
    }
}

// Change member role / remove member
if (window.location.href.includes('members')) {
    modalToggle('.changeRoleBtn', 'changeRoleModal', 'closeRoleChangeModal')
    modalToggle('.removeMemberBtn', 'removeMemberModal', 'closeRemoveMemberModal')
} 

// Leave account
if (window.location.href.includes('manage')) {
    modalToggle('.leaveCommunityBtn', 'leaveCommAccountModal', 'closeLeaveCommModal')
    modalToggle('.leaveInstitutionBtn', 'leaveInstAccountModal', 'closeLeaveInstModal')
} 

// Create institution: non-ROR modal
if (window.location.href.includes('create-institution')) {
    const closeNORORModalBtn = document.getElementById('closeNORORmodal')
    let modal = document.getElementById('noRORModal')
    const openNORORModalBtn = document.getElementById('openNORORModalBtn')

    openNORORModalBtn.addEventListener('click', function() { modal.classList.replace('hide', 'show')})
    closeNORORModalBtn.addEventListener('click', function(e)  {
        e.preventDefault()
        modal.classList.replace('show', 'hide')
    } )
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

// REGISTRY FILTERING AND JOIN REQUESTS / CONTACT MODAL
if (window.location.href.includes('registry')) {

    // Send request to join institution or community
    const registryModal = document.getElementById('registryModal')
    const submitJoinRequestFormBtn = document.getElementById('submitRegistryForm')

    const closeRegistryModalBtn = document.getElementById('closeRegistryModal')
    closeRegistryModalBtn.addEventListener('click', function(e) { registryModal.classList.replace('show', 'hide') })

    document.addEventListener('click', function(e) {

        if (e.target.tagName == 'A') {
            // get Id and btn type, based on which organization it is, submit
            if (e.target.id.includes('communityRequest')) {
                // show modal
                registryModal.classList.replace('hide', 'show')
                let targetId = e.target.id.split('-').pop()
                submitJoinRequestFormBtn.addEventListener('click', function(e) { 
                    disbleSendRequestBtn(submitJoinRequestFormBtn)
                    document.getElementById(`communityRegistryForm${targetId}`).submit() 
                })    
            } else if (e.target.id.includes('institutionRequest')) {
                // show modal
                registryModal.classList.replace('hide', 'show')
                let targetId = e.target.id.split('-').pop()
                submitJoinRequestFormBtn.addEventListener('click', function(e) { 
                    disbleSendRequestBtn(submitJoinRequestFormBtn)
                    document.getElementById(`institutionRegistryForm${targetId}`).submit() 
                })  

                // open contact form modal
            } else if (e.target.id.includes('communityContact')) {
                let targetId = e.target.id.split('-').pop()
                let modal = document.getElementById(`contactModalComm${targetId}`)
                modal.classList.replace('hide', 'show')
                closeModal(modal)

            } else if (e.target.id.includes('institutionContact')) {
                let targetId = e.target.id.split('-').pop()
                let modal = document.getElementById(`contactModalInst${targetId}`)
                modal.classList.replace('hide', 'show')
                closeModal(modal)
                
            } else if (e.target.id.includes('researcherContact')) {
                let targetId = e.target.id.split('-').pop()
                let modal = document.getElementById(`contactModalResearcher${targetId}`)
                modal.classList.replace('hide', 'show')
                closeModal(modal)
            }
        }
    })  

    // Temporarily disable the submit button to prevent multiple form submission
    function disbleSendRequestBtn(btn) {
        let oldValue = 'Yes'
        btn.setAttribute('disabled', true)
        btn.classList.replace('action-btn', 'disabled-btn')
        btn.innerText = 'Sending'
    
        setTimeout(function(){
            btn.innerText = oldValue;
            btn.classList.replace('disabled-btn', 'action-btn')
            btn.removeAttribute('disabled');
        }, 9000)
    }

    function closeModal(modal) {  
        let closeBtns = Array.from(document.getElementsByClassName('close-modal-btn'))
        closeBtns.forEach(btn => { btn.addEventListener('click', hideModal)})
        function hideModal () { modal.classList.replace('show', 'hide') }
    }
}

// PROJECTS FILTERING
if (window.location.href.includes('projects')) {
    const filterbyNotices = document.getElementById('filterProjectsWithNotices')
    const filterbyLabels = document.getElementById('filterProjectsWithLabels')
    const filterbyAll = document.getElementById('filterAll')

    if (filterbyNotices && filterbyLabels && filterbyAll) {
        filterbyNotices.addEventListener('click', () => hideProjectsWithoutNotices())
        filterbyLabels.addEventListener('click', () => hideProjectsWithoutLabels())
        filterbyAll.addEventListener('click', () => showAllProjects())
    }

    // Hidden inputs to track which projects have Labels or Notices
    let hiddenInputNotices = document.querySelectorAll('.projectNoticesFilter')
    let hiddenInputLabels = document.querySelectorAll('.projectLabelsFilter')

    // Initialize array to store the project ids
    let projectsWithLabelsIDs = []
    let projectsWithNoticesIDs = []

    // shows Projects with Notices
    let hideProjectsWithoutNotices = () => {
        filterbyNotices.classList.add('bold')
        if (filterbyLabels.classList.contains('bold')) { filterbyLabels.classList.remove('bold')}
        if (filterbyAll.classList.contains('bold')) { filterbyAll.classList.remove('bold')}

        // Add ID to array from hidden inputs
        hiddenInputLabels.forEach(label => { projectsWithLabelsIDs.push(label.id.substring(6))})

        projectsWithLabelsIDs.forEach(id => {
            let targetProjectDiv = document.getElementById(`full-div-card-${id}`)
            targetProjectDiv.classList.replace('show', 'hide')
        })

        projectsWithNoticesIDs.forEach(id => { 
            let targetProjectDiv = document.getElementById(`full-div-card-${id}`)
            targetProjectDiv.classList.replace('hide', 'show')
        })
    }

    // shows projects with Labels
    let hideProjectsWithoutLabels = () => {
        filterbyLabels.classList.add('bold')
        if (filterbyNotices.classList.contains('bold')) { filterbyNotices.classList.remove('bold')}
        if (filterbyAll.classList.contains('bold')) { filterbyAll.classList.remove('bold')}

        // Add ID to array from hidden inputs
        hiddenInputNotices.forEach(notice => { projectsWithNoticesIDs.push(notice.id.substring(7))})
        
        projectsWithNoticesIDs.forEach(id => { 
            let targetProjectDiv = document.getElementById(`full-div-card-${id}`)
            targetProjectDiv.classList.replace('show', 'hide')
        })

        projectsWithLabelsIDs.forEach(id => { 
            let targetProjectDiv = document.getElementById(`full-div-card-${id}`)
            targetProjectDiv.classList.replace('hide', 'show')
        })
    }

    // Shows all projects
    let showAllProjects = () => {
        filterbyAll.classList.add('bold')
        if (filterbyNotices.classList.contains('bold')) { filterbyNotices.classList.remove('bold')}
        if (filterbyLabels.classList.contains('bold')) { filterbyLabels.classList.remove('bold')}

        let allProjectDivs = document.querySelectorAll('.filterProjects')
        allProjectDivs.forEach(div => { div.classList.replace('hide', 'show') })
    }
}

//  ONBOARDING MODAL: Shows up in dashboard if there isn't a localstorage item saved and onboarding_on is set to true
if (window.location.href.includes('dashboard')) {
    const hiddenInput = document.getElementById('openOnboarding')
    const onboardingModal = document.getElementById('onboardingModal')
    const closeOnboardBtns = document.querySelectorAll('.close-onboarding-btn')
    const nextBtns = document.querySelectorAll('.btn-next')
    const backBtns = document.querySelectorAll('.btn-back')
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

    backBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            modalStepsNum--
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

    // When 'tutorial' is clicked, removes localstorage item so onboarding can pop up
    const onboardingOn = document.getElementById('onboardingOn')
    onboardingOn.addEventListener('click', function() {
        localStorage.removeItem('closedOnboarding')
    })
}

// addURLModal
if (window.location.href.includes('notices')) { 
    const modal = document.getElementById('addURLModal')
    const addURLBtn = document.getElementById('addURLBtn')

    addURLBtn.addEventListener('click', () => {
        if (modal.classList.contains('hide')) { modal.classList.replace('hide', 'show')}
    })

    const closeModalBtn = document.querySelector('.close-modal-btn')
    closeModalBtn.addEventListener('click', function() { modal.classList.replace('show', 'hide')})
}