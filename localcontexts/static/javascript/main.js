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

// Show customised label text in community: labels
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

// BC Content
var provenanceName = 'BC Provenance (BC P)'
var multipleCommunityName = 'BC Multiple Communities (BC MC)'
var openToCollabName = 'BC Open to Collaboration (BC OC)'
var openToCommercializationName = ' BC Open to Commercialization (BC C)'
var researchUseName = 'BC Research Use (BC R)'
var consentVerifiedName = 'BC Consent Verified (BC CV)'

var provenanceUse = 'Indigenous peoples have the right to make decisions about the future use of information, biological collections, data and digital sequence information (DSI) that derives from associated lands, waters and territories. This Label supports the practice of proper and appropriate acknowledgement into the future.'
var multipleCommUse = 'This Label should be used to indicate that multiple communities have responsibility, custodianship and/or ownership over the geographic regions where this species or biological entity originates/is found. This Label recognizes that whilst one community might exert specific authority, other communities also have rights and responsibilities for use and care.'
var openToCollabUse = 'This Label is being used to indicate that the community is open to research collaborations and outreach activities. With this Label, future opportunities for collaboration and engagement are supported.'
var openToCommUse = 'Indigenous peoples have the right to benefit from information, biological collections, data and digital sequence information (DSI) that derives from traditional lands, waters and territories. This Label is being used to indicate the express interest that [community name or authorizing party] has in being a primary party to any future negotiations if future commercialization opportunities arise from these resources.'
var researchUse = 'This label should be used for permissioning the use of information, collections, data and digital sequence information for unspecified research. The research use label does not give permission for commercialization activities.'
var consentVerifiedUse = 'Indigenous peoples have the right to permission the use of information, biological collections, data and digital sequence information (DSI) that derives from associated lands, waters and territories. This Label verifies that there are consent conditions in place for uses of information, collections, data and digital sequence information.'

var provenanceText = 'This Label is being used to affirm an inherent interest Indigenous people have in the scientific collections and data about communities, peoples, and the biodiversity found within traditional lands, waters and territories. [Community name or authorizing party] has permissioned the use of this collection and associated data for research purposes, and retains the right to be named and associated with it into the future. This association reflects a significant relationship and responsibility to [the species or biological entity] and associated scientific collections and data.'
var multipleCommunityText = 'This Label is being used to affirm responsibility and ownership over this information, collection, data and digital sequence information is spread across several distinct communities. Use will be dependent upon discussion and negotiation with multiple communities.'
var openToCollabText = 'This Label is being used to make clear [community name or authorizing body] is open to future engagement, collaboration, and partnership around research and outreach opportunities.'
var openToCommercializationText = 'This Label is being used to indicate that [community name or authorizing party] is open to commercialization opportunities that might derive from any information, collections, data and DSI to which this Label is connected. As a primary party in any partnership and collaboration opportunities that emerge from the use of these resources, we retain an express interest in any future negotiations.'
var researchUseText = 'This Label is being used by [community name or authorizing body] to allow this information, collection, data and digital sequence information to be used for unspecified research purposes. This Label does not provide permission for commercialization activities.  [Optional return of research results statement].'
var consentVerifiedText = 'This Label is being used to verify that [community name or authorizing party] have consent conditions in place for the use of this information, collections, data and digital sequence information.'


// TK Content
var tkAttributionName = 'TK Attribution (TK A)'
var tkClanName = 'TK Clan (TK CL)'
var tkFamilyName = 'TK Family (TK F)'
var tkMultipleCommunityName = 'TK Multiple Communities (TK MC)'
var tkOutreachName = 'TK Outreach (TK O)'
var tkNonVerifiedName = 'TK Non-Verified (TK NV)'
var tkVerifiedName = 'TK Verified (TK V)'
var tkNonCommercialName = 'TK Non-Commercial (TK NC)'
var tkCommercialName = 'TK Commercial (TK C)'
var tkCulturallySensitiveName = 'TK Culturally Sensitive (TK CS)'
var tkCommunityVoiceName = 'TK Community Voice (TK CV)'
var tkCommunityUseOnlyName = 'TK Community Use Only (TK CO)'
var tkSeasonalName = 'TK Seasonal (TK S)'
var tkWomenGeneralName = 'TK Women General (TK WG)'
var tkMenGeneralName = 'TK Men General (TK MG)'
var tkMenRestrictedName = 'TK Men Restricted (TK MR)'
var tkWomenRestrictedName = 'TK Women Restricted (TK WR)'
var tkSecretSacredName = 'TK Secret / Sacred (TK SS)'

var tkAttributionUse = 'This label should be used when you would like anyone who uses this material to know who the correct sources, custodians, owners are. This is especially useful if this material has been wrongly attributed or important names of the people involved in making this material or safeguarding this material, are missing. This label allows you to correct historical mistakes in terms of naming and acknowledging the legitimate authorities for this material. This label asks for future users to also apply the correct names and attribution.'
var tkClanUse = 'This Label should be used when you would like external users to know that this material is subject to conditions for circulation relating to clan membership and or is according to protocols for clan relationships. Because these conditions have not historically been recognized, this Label helps make these conditions for use and circulation clearer. Specifically, the Label asks future users to respect culturally specific rules of use and to make informed decisions about using this type of material.'
var tkFamilyUse = 'This label should be used when you would like external users to know that this material is subject to certain conditions for circulation. This material is usually only shared between family members. Because these conditions have not historically been recognized, this label helps make these conditions clearer for future users. Specifically it asks them to respect culturally specific rules of use and to make different and fair decisions about using this type of material.'
var tkMultipleCommunityUse = 'This label should be used to indicate that multiple communities have responsibilities of custodianship and/or ownership over specific material. This label recognizes that no singular community has explicit control. Rather, rights and responsibilities for use are spread across communities through already existing community protocols and ongoing cultural relationships.'
var tkOutreachUse = 'This label should be used when you would only like your cultural materials used for educational outreach activities. Outreach activities means to share works outside the community in order to increase and raise awareness and education about your family, clan and/or community. Sites for outreach activities can include schools, universities, libraries, archives, museums, online forums and small learning groups. Depending on what kind of context and the possibilities for increased circulation of this material, this label helps TK holders and users to develop new possibilities in the fair and equitable reciprocal exchange for use of this material in outreach activities. This exchange might include access to educational or other resources that your community has difficulty accessing under other circumstances.'
var tkNonVerifiedUse = 'This material has not been verified by the community. Reasons for this could include that it has not been appropriately vetted, has mistakes, omissions, derogatory language, lack of informed consent, or its process of creation was through dishonest research which did not follow proper community protocols.'
var tkVerifiedUse = 'This label should be used when you and your community are satisfied with the way in which your traditional knowledge materials are being represented online or offline. This label affirms that appropriate conditions for access and use are in place and that whoever has made this material accessible has made accommodations for cultural protocols associated with the knowledge. It lets users know that the right thing is being done by your community protocols and standards.'
var tkNonCommercialUse = 'This label should be used when you would like to let external users who have access to your material know that it should only be used in non-commercial ways. You are asking users to be respectful and fair with your cultural materials and ask that it not be used to derive economic benefits or used in any way that makes it into a commodity for sale or purchase.'
var tkCommercialUse = 'This label should be used when you are happy for an external user to use your cultural material in any way, including deriving future economic benefit. With commercial use you will have no control over how the work is circulated. We would encourage you to establish contact information to help you have direct negotiations with those external parties who would like to use your work under this label. This is in order to help prevent derogatory treatment and cultural offense.'
var tkCulturallySensitiveUse = 'This Label should be used when you would like external users to know that this material has special sensitivities around it and should be treated with great care. These sensitivities could include: that it has only recently been reconnected with the community from which it originates, that the community is currently vetting and spending time with the material, and/or that the material is culturally valued and needs to be kept safe. This Label could also be used to indicate that there are cultural sensitivities around this material arising from legacies of colonialism, for instance, the use of derogatory language or descriptive errors within the content and/or content descriptions.'
var tkCommunityVoiceUse = 'This Label should be used when you would like to encourage community members to share their knowledge, stories and experiences. This Label would usually be used within a community-based archive to encourage the sharing of stories. This Label indicates that the current narrative or explanation that accompanies this material is incomplete or partial and that many community voices are needed to help make sense and understand the event, photograph, recording or heritage item. The Community Voice Label encourages multiplicity in the telling, listening and sharing of community histories and cultural knowledge.'
var tkCommunityUseOnlyUse = 'This label should be used when you would like external users to know that this material is subject to certain conditions of circulation namely that this material is usually not circulated beyond the family, clan or community. Because these conditions have not historically been recognized, this label helps make these conditions clearer for future users. Specifically it asks them to respect culturally specific rules of use and to make different and fair decisions about using this type of material.'
var tkSeasonalUse = 'This label should be used when you want to let external users know that the material that is openly circulating has seasonal conditions of access and use. This could mean that some material should only be used and heard at particular times of the year. It could also mean that the environment and land where this material derives also influences and impacts its meaning and significance. This label can be used to help external users know that there are land-based teachings in this material which affect proper use and respectful understanding.'
var tkWomenGeneralUse = 'This label should be used when you want to let external users know that the material circulating should only be shared between women in the community. This is a women’s general label and indicates that there are restrictions of access and use to women within the community based on customary law. This label can be used to help external users recognize that with this material there are specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge can only be shared among specific members of the community. It should be used to complement already existing customs and protocols of access and use.'
var tkMenGeneralUse = 'This label should be used when you want to let external users know that the material circulating should only be shared between men in the community. This is a men’s general label and indicates that there are restrictions of access and use to men based on customary law. This label can be used to help external users recognize that with this material there are specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge can only be shared among specific members of the community. It should be used to complement already existing customs and protocols of access and use.'
var tkMenRestrictedUse = 'This label should be used when you want to let external users know that the material circulating freely is actually of a highly restricted nature. This is a men’s highly restricted label and indicates that there are restrictions of access and use based on customary law. This label can be used to help external users recognize that with this material there are very specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge expressions can only be shared among specific members of the community. Only authorized [and/or initiated] men within the community should be using this material.'
var tkWomenRestrictedUse = 'This label should be used when you want to let external users know that the material circulating freely is actually of a highly restricted nature. This is a women’s highly restricted label and indicates that there are restrictions of access and use based on customary law. This label can be used to help external users recognize that with this material there are very specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge expressions can only be shared among specific members of the community. Only authorized [and/or initiated] women within the community should be using this material.'
var tkSecretSacredUse = 'This label should be used when you want to let external users know that the material that is openly circulating contains secret/sacred information and that it has specific conditions of access and use. These conditions potentially include restrictions upon access. Using this label helps to alert external users that this material is special and requires respectful and careful treatment. It asks users to make different decisions about using it and, importantly, to discuss any potential use with you.'

var tkAttributionText = 'This label is being used to correct historical mistakes or exclusions pertaining to this material. This is especially in relation to the names of the people involved in performing or making this work and/or correctly naming the community from which it originally derives. As a user you are being asked to also apply the correct attribution in any future use of this work.'
var tkClanText = 'This Label is being used to indicate that this material is traditionally and usually not publicly available. The Label lets future users know that this material has specific conditions for use and sharing because of clan membership and/or relationships. This material is not, and never was, free, public and available for everyone. This Label asks viewers of these materials to respect the cultural values and expectations about circulation and use defined by designated clans, members and their internal relations.'
var tkFamilyText = 'This label is being used to indicate that this material is traditionally and usually not publicly available. The label is correcting a misunderstanding about the circulation options for this material and letting any users know that this material has specific conditions for sharing between family members. Who these family members are, and how sharing occurs will be defined in each locale. This material is not, and never was, free, public and available for everyone at anytime. This label asks you to think about how you are going to use this material and to respect different cultural values and expectations about circulation and use.'
var tkMultipleCommunityText = 'Responsibility and ownership over this material is spread across several distinct communities. Use will be dependent upon discussion and negotiation with the multiple communities named herein [insert names]. Decisions about use will need to be decided collectively. As an external user of this material you are asked to recognize and respect cultural protocols in relation to the use of this material and clear your intended use with the relevant communities.'
var tkOutreachText = 'This label is being used to indicate that this material is traditionally and usually not publicly available. The label is correcting a misunderstanding about the circulation options for this material and letting any users know that this material can be used for educational outreach activities. This label asks you to respect the designated circulation conditions for this material and additionally, where possible, to develop a means for fair and equitable reciprocal exchange for the use of this material with the relevant TK holders. This exchange might include access to educational or other resources that are difficult to access under normal circumstances.'
var tkNonVerifiedText = 'This Label is being used because there are concerns about accuracy and/or representations made in this material. This material was not created through informed consent or community protocols for research and engagement. Therefore questions about its accuracy and who/how it represents this community are being raised.'
var tkVerifiedText = 'This label affirms that the representation and presentation of this material is in keeping with community expectations and cultural protocols. It lets you know that for the individual, family or community represented in this material, use is considered fair, reasonable and respectful.'
var tkNonCommercialText = 'This material has been designated as being available for non-commercial use. You are allowed to use this material for non-commercial purposes including for research, study or public presentation and/or online in blogs or non-commercial websites. This label asks you to think and act with fairness and responsibility towards this material and the original custodians.'
var tkCommercialText = 'This material is available for commercial use. While the source community does not have copyright ownership of this material, it may still be protected under copyright and any commercial use will need to be cleared with the copyright holder. Regardless of the copyright ownership, you are asked to pay special attention to the community’s protocols and not use this material in any way that could constitute derogatory treatment and/or any other use that could constitute community or cultural harm. Where necessary, contact information is provided to help you enter into a dialogue with the original custodians and to clarify that your use will not be derogatory or cause cultural offense.'
var tkCulturallySensitiveText = 'This Label is being used to indicate that this material has cultural and/or historical sensitivities. The label asks for care to be taken when this material is accessed, used, and circulated, especially when materials are first returned or reunited with communities of origin. In some instances, this label will indicate that there are specific permissions for use of this material required directly from the community itself.'
var tkCommunityVoiceText = 'This Label is being used to encourage the sharing of stories and voices about this material. The Label indicates that existing knowledge or descriptions are incomplete or partial. Any community member is invited and welcome to contribute to our community knowledge about this event, photograph, recording or heritage item. Sharing our voices helps us reclaim our histories and knowledge. This sharing is an internal process.'
var tkCommunityUseOnlyText = 'This label is being used to indicate that this material is traditionally and usually not publicly available. The label is correcting a misunderstanding about the circulation options for this material and letting any users know that this material has specific conditions for circulation within the community. It is not, and never was, free, public and available for everyone at anytime. This label asks you to think about how you are going to use this material and to respect different cultural values and expectations about circulation and use.'
var tkSeasonalText = 'This label is being used to indicate that this material traditionally and usually is heard and/or utilized at a particular time of year and in response to specific seasonal changes and conditions. For instance, many important ceremonies are held at very specific times of the year. This label is being used to indicate sophisticated relationships between land and knowledge creation. It is also being used to highlight the relationships between recorded material and the specific contexts where it derives, especially the interconnected and embodied teachings that it conveys.'
var tkWomenGeneralText = 'This material has specific gender restrictions on access. It is usually only to be accessed and used by women in the community. If you are not from the community and you have accessed this material, you are requested not to download, copy, remix or otherwise circulate this material to others without permission. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkMenGeneralText = 'This material has specific gender restrictions on access. It is usually only to be accessed and used by men in the community. If you are not from the community and you have accessed this material, you are requested to not download, copy, remix or otherwise circulate this material to others without permission. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkMenRestrictedText = 'This material has specific gender restrictions on access. It is regarded as important secret and/or ceremonial material that has community-based laws in relation to who can access it. Given its nature it is only to be accessed and used by authorized [and initiated] men in the community. If you are an external third party user and you have accessed this material, you are requested to not download, copy, remix or otherwise circulate this material to others. This material is not freely available within the community and it therefore should not be considered freely available outside the community. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkWomenRestrictedText = 'This material has specific gender restrictions on access. It is regarded as important secret and/or ceremonial material that has community-based laws in relation to who can access it. Given its nature it is only to be accessed and used by authorized [and initiated] women in the community. If you are an external third party user and you have accessed this material, you are requested to not download, copy, remix or otherwise circulate this material to others. This material is not freely available within the community and it therefore should not be considered freely available outside the community. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkSecretSacredText = 'This label is being used to indicate that this material is traditionally and usually not publicly available because it contains important secret or sacred components. The label is correcting a misunderstanding about the significance of this material and therefore its circulation conditions. It is letting users know that because of its secret/sacred status it is not, and was never free, public and available for everyone at anytime. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'


// Expand BC Labels Card in Community: Labels -> select-labels
function showBCLabelInfo() {
    let labelContainer = document.getElementById('expand-bclabels')
    let span = document.getElementById('show-more-down')
    let fullCard = document.getElementById('collapsed-card')
    let header = document.getElementById('bclabels-title-vertical')

    if (labelContainer.style.height == "0px") {
        // header.style.margin = "0"
        // fullCard.style.height = "460px"
        // fullCard.style.transition = "height 0.5s"
        // labelContainer.style.height = "460px"

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

    // Expand full card
    let info = document.getElementById('bclabel-info')
    let fullCard = document.getElementById('collapsed-card')
    let labelContainer = document.getElementById('expand-bclabels')

    if (info.style.height == "0px") {
        labelContainer.style.height = "auto"
        info.style.height = "auto"
        fullCard.style.height = "auto"
    } else {
        labelContainer.style.height = "auto"
        info.style.height = "0px"
        fullCard.style.height = "auto"
    }

    // Set content based on which Label was selected
    let targetImg = img.id
    let title = document.getElementById('bc-label-title')
    let templateText = document.getElementById('label-template-text')
    let whyUseLabelText = document.getElementById('why-use-this-label')

    switch (targetImg) {
        case 'bcr':
            whichBCImgClicked('bcr')
            title.textContent = researchUseName
            templateText.textContent = researchUseText
            whyUseLabelText.textContent = researchUse
            break;
        case 'bccv':
            whichBCImgClicked('bccv')
            title.textContent = consentVerifiedName
            templateText.textContent = consentVerifiedText
            whyUseLabelText.textContent = consentVerifiedUse
            break;
        case 'bcocomm':
            whichBCImgClicked('bcocomm')
            title.textContent = openToCommercializationName
            templateText.textContent = openToCommercializationText
            whyUseLabelText.textContent = openToCommUse
            break;
        case 'bcocoll':
            whichBCImgClicked('bcocoll')
            title.textContent = openToCollabName
            templateText.textContent = openToCollabText
            whyUseLabelText.textContent = openToCollabUse
            break;
        case 'bcmc':
            whichBCImgClicked('bcmc')
            title.textContent = multipleCommunityName
            templateText.textContent = multipleCommunityText
            whyUseLabelText.textContent = multipleCommUse
            break;
        case 'bcp':
            whichBCImgClicked('bcp')
            title.textContent = provenanceName
            templateText.textContent = provenanceText
            whyUseLabelText.textContent = provenanceUse
            break;
    }

}

//  Assign input value based on which bc label image is selected in Community: select-abels
function whichBCImgClicked(val) {
    var input = document.getElementById('bc-label-value-type')
    input.value = val
}

// Assign input value based on which bc label image is selected in Community: select-labels
function whichTKImgClicked(val) {
    var inputProv = document.getElementById('tk-label-value-type-prov')
    var inputProt = document.getElementById('tk-label-value-type-prot')
    var inputPerms = document.getElementById('tk-label-value-type-perms')

    if(val == 'tka' || val == 'tkcl' || val == 'tkf' || val == 'tkmc') {
        inputProv.value = val
    } else if (val == 'tks' || val == 'tkwg' || val == 'tkmg' || val == 'tkmr' || val == 'tkwr' || val == 'tkcs' || val == 'tkss') {
        inputProt.value = val
    } else if (val == 'tkv' || val == 'tknv' || val == 'tkc' || val == 'tknc' || val == 'tkcv' || val == 'tkco' || val == 'tko') {
        inputPerms.value = val
    }
}


// Community: Customise labels -- populate default text
var parentDiv = document.getElementById('target-img-div')
if (parentDiv) {
    var image = parentDiv.firstChild.nextSibling
    populateTemplate(image.id)
}

function populateTemplate(id) {
    let title = document.getElementById('label-title-name')
    let templateText = document.getElementById('label-template-text')

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
    
        case 'tka':
            title.value = tkAttributionName
            templateText.textContent = tkAttributionText
            break;
        case 'tkcl':
            title.value = tkClanName
            templateText.textContent = tkClanText
            break;
        case 'tkf':
            title.value = tkFamilyName
            templateText.textContent = tkFamilyText
            break;
        case 'tkmc':
            title.value = tkMultipleCommunityName
            templateText.textContent = tkMultipleCommunityText
            break;
        case 'tko':
            title.value = tkOutreachName
            templateText.textContent = tkOutreachText
            break;
        case 'tknv':
            title.value = tkNonVerifiedName
            templateText.textContent = tkNonVerifiedText
            break;
        case 'tkv':
            title.value = tkVerifiedName
            templateText.textContent = tkVerifiedText
            break;
        case 'tknc':
            title.value = tkNonCommercialName
            templateText.textContent = tkNonCommercialText
            break;
        case 'tkc':
            title.value = tkCommercialName
            templateText.textContent = tkCommercialText
            break;
        case 'tkcs':
            title.value = tkCulturallySensitiveName
            templateText.textContent = tkCulturallySensitiveText
            break;
        case 'tkcv':
            title.value = tkCommunityVoiceName
            templateText.textContent = tkCommunityVoiceText
            break;
        case 'tkco':
            title.value = tkCommunityUseOnlyName
            templateText.textContent = tkCommunityUseOnlyText
            break;
        case 'tks':
            title.value = tkSeasonalName
            templateText.textContent = tkSeasonalText
            break;
        case 'tkwg':
            title.value = tkWomenGeneralName
            templateText.textContent = tkWomenGeneralText
            break;
        case 'tkmg':
            title.value = tkMenGeneralName
            templateText.textContent = tkMenGeneralText
            break;
        case 'tkmr':
            title.value = tkMenRestrictedName
            templateText.textContent = tkMenRestrictedText
            break;
        case 'tkwr':
            title.value = tkWomenRestrictedName
            templateText.textContent = tkWomenRestrictedText
            break;
        case 'tkss':
            title.value = tkSecretSacredName
            templateText.textContent = tkSecretSacredText
            break;
                                                                                                                
    }

}

// Community: Activity
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
// Community: Activity : apply labels
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


// TK Labels : community -> customise -> select labels
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

    console.log(targetImg)

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

    switch (targetImg) {
        // Provenance Labels
        case 'tka':
            openInfoDiv(infoProv)
            whichTKImgClicked('tka')
            titleProv.textContent = tkAttributionName
            templateTextProv.textContent = tkAttributionText
            whyUseLabelTextProv.textContent = tkAttributionUse
            break;
        case 'tkcl':
            openInfoDiv(infoProv)
            whichTKImgClicked('tkcl')
            titleProv.textContent = tkClanName
            templateTextProv.textContent = tkClanText
            whyUseLabelTextProv.textContent = tkClanUse
            break;
        case 'tkf':
            openInfoDiv(infoProv)
            whichTKImgClicked('tkf')
            titleProv.textContent = tkFamilyName
            templateTextProv.textContent = tkFamilyText
            whyUseLabelTextProv.textContent = tkFamilyUse
            break;
        case 'tkmc':
            openInfoDiv(infoProv)
            whichTKImgClicked('tkmc')
            titleProv.textContent = tkMultipleCommunityName
            templateTextProv.textContent = tkMultipleCommunityText
            whyUseLabelTextProv.textContent = tkMultipleCommunityUse
            break;

        // Protocols Labels
        case 'tks':
            openInfoDiv(infoProt)
            whichTKImgClicked('tks')
            titleProt.textContent = tkSeasonalName
            templateTextProt.textContent = tkSeasonalText
            whyUseLabelTextProt.textContent = tkSeasonalUse
            break;
        case 'tkwg':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkwg')
            titleProt.textContent = tkWomenGeneralName
            templateTextProt.textContent = tkWomenGeneralText
            whyUseLabelTextProt.textContent = tkWomenGeneralUse
            break;
        case 'tkmg':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkmg')
            titleProt.textContent = tkMenGeneralName
            templateTextProt.textContent = tkMenGeneralText
            whyUseLabelTextProt.textContent = tkMenGeneralUse
            break;
        case 'tkmr':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkmr')
            titleProt.textContent = tkMenRestrictedName
            templateTextProt.textContent = tkMenRestrictedText
            whyUseLabelTextProt.textContent = tkMenRestrictedUse
            break;
        case 'tkwr':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkwr')
            titleProt.textContent = tkWomenRestrictedName
            templateTextProt.textContent = tkWomenRestrictedText
            whyUseLabelTextProt.textContent = tkWomenRestrictedUse
            break;
        case 'tkcs':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkcs')
            titleProt.textContent = tkCulturallySensitiveName
            templateTextProt.textContent = tkCulturallySensitiveText
            whyUseLabelTextProt.textContent = tkCulturallySensitiveUse
            break;
        case 'tkss':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkss')
            titleProt.textContent = tkSecretSacredName
            templateTextProt.textContent = tkSecretSacredText
            whyUseLabelTextProt.textContent = tkSecretSacredUse
            break;

        // Permissions Labels
        case 'tko':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tko')
            titlePerms.textContent = tkOutreachName
            templateTextPerms.textContent = tkOutreachText
            whyUseLabelTextPerms.textContent = tkOutreachUse
            break;
        case 'tknv':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tknv')
            titlePerms.textContent = tkNonVerifiedName
            templateTextPerms.textContent = tkNonVerifiedText
            whyUseLabelTextPerms.textContent = tkNonVerifiedUse
            break;
        case 'tkv':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkv')
            titlePerms.textContent = tkVerifiedName
            templateTextPerms.textContent = tkVerifiedText
            whyUseLabelTextPerms.textContent = tkVerifiedUse
            break;
        case 'tknc':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tknc')
            titlePerms.textContent = tkNonCommercialName
            templateTextPerms.textContent = tkNonCommercialText
            whyUseLabelTextPerms.textContent = tkNonCommercialUse
            break;
        case 'tkc':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkc')
            titlePerms.textContent = tkCommercialName
            templateTextPerms.textContent = tkCommercialText
            whyUseLabelTextPerms.textContent = tkCommercialUse
            break;
        case 'tkcv':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkcv')
            titlePerms.textContent = tkCommunityVoiceName
            templateTextPerms.textContent = tkCommunityVoiceText
            whyUseLabelTextPerms.textContent = tkCommunityVoiceUse
            break;
        case 'tkco':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkco')
            titlePerms.textContent = tkCommunityUseOnlyName
            templateTextPerms.textContent = tkCommunityUseOnlyText
            whyUseLabelTextPerms.textContent = tkCommunityUseOnlyUse
            break;
    }

}

// RESEARCHERS
// Notices

function expandNotices() {
    let showMoreSpan = document.getElementById('show-more-notices')
    let fullCard = document.getElementById('expand-notice-card')
    let tkDiv = document.getElementById('tk-notice-expand-txt')
    let bcDiv = document.getElementById('bc-notice-expand-txt')
    let topDiv = document.getElementById('border-bottom-div')
    let bcTextDiv = document.getElementById('bc-notice-expand-txt')
    let tkTextDiv = document.getElementById('tk-notice-expand-txt')


    if (tkDiv.style.height == '0px' && bcDiv.style.height == '0px') {
        showMoreSpan.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
        tkDiv.style.height = 'auto'
        fullCard.style.height = 'auto'
        topDiv.classList.add('border-bottom-dash-teal')
        tkTextDiv.classList.add('border-bottom-dash-teal')
    } else {
        showMoreSpan.innerHTML = `Show More <i class="fa fa-angle-down" aria-hidden="true"></i>`
        fullCard.style.height = '385px'
        tkDiv.style.height = '0px'
        bcDiv.style.height = '0px'
        topDiv.classList.remove('border-bottom-dash-teal')
        bcTextDiv.classList.remove('border-bottom-dash-teal')
        tkTextDiv.classList.remove('border-bottom-dash-teal')
    }
}


function expandNoticeText(img) {
    let bcTextDiv = document.getElementById('bc-notice-expand-txt')
    let tkTextDiv = document.getElementById('tk-notice-expand-txt')
    let topDiv = document.getElementById('border-bottom-div')
    let showMoreSpan = document.getElementById('show-more-notices')
    let fullCard = document.getElementById('expand-notice-card')

    if (tkTextDiv.style.height == 'auto' || bcTextDiv.style.height == 'auto') {
        topDiv.classList.add('border-bottom-dash-teal')
        showMoreSpan.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    } else {
        topDiv.classList.remove('border-bottom-dash-teal')
        showMoreSpan.innerHTML = `Show Less <i class="fa fa-angle-up" aria-hidden="true"></i>`
    }

    if (img.id == 'bc-notice') {
        bcTextDiv.style.height = 'auto'
        fullCard.style.height = 'auto'
        topDiv.classList.add('border-bottom-dash-teal')
        bcTextDiv.classList.add('border-bottom-dash-teal')
    } else {
        bcTextDiv.style.height = '0px'
        bcTextDiv.style.overflow = 'hidden'
        bcTextDiv.classList.remove('border-bottom-dash-teal')
    }
    
    if (img.id == 'tk-notice') {
        tkTextDiv.style.height = 'auto'
        fullCard.style.height = 'auto'
        topDiv.classList.add('border-bottom-dash-teal')
        tkTextDiv.classList.add('border-bottom-dash-teal')
    } else {
        tkTextDiv.style.height = '0px'
        tkTextDiv.style.overflow = 'hidden'
        tkTextDiv.classList.remove('border-bottom-dash-teal')
    }
}

// Institutions: create-projects : show notice descriptions
function showDescription() {
    let bcInput = document.getElementById('bc-notice')
    let tkInput = document.getElementById('tk-notice')
    let tkDescriptionDiv = document.getElementById('show-notice-description-tk')
    let bcDescriptionDiv = document.getElementById('show-notice-description-bc')

    let tkTarget = tkInput.parentElement.nextElementSibling.nextElementSibling.firstElementChild
    let bcTarget = bcInput.parentElement.nextElementSibling.nextElementSibling.firstElementChild

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

// Communities: Activity: Notify 
function setBCNoticeUUID(elem) {
    let elementId = elem.id
    let statusSelect = document.getElementById(elementId)
    let noticeIdInput = document.getElementById('notice-id-input')
    let statusSelectedInput = document.getElementById('status-selection-input')
    let noticeID = elementId.slice(7)

    // Set first hidden value to notice UUID
    noticeIdInput.value = noticeID
    // Set second hidden value to value of option selected
    statusSelectedInput.value = statusSelect.options[statusSelect.selectedIndex].value
}

// Communities: Activity: Notify 
function setTKNoticeUUID(elem) {
    let elementId = elem.id
    let statusSelect = document.getElementById(elementId)
    let noticeIdInput = document.getElementById('tknotice-id-input')
    let statusSelectedInput = document.getElementById('tkstatus-selection-input')
    let noticeID = elementId.slice(7)

    // Set first hidden value to notice UUID
    noticeIdInput.value = noticeID
    // Set second hidden value to value of option selected
    statusSelectedInput.value = statusSelect.options[statusSelect.selectedIndex].value
}

// Require Checkbox selection for Notices
// h/t: https://vyspiansky.github.io/2019/07/13/javascript-at-least-one-checkbox-must-be-selected/
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

// TODO: Add ROR functionality
// Create Institution
// const endpoint = `http://api.ror.org/organizations`
// const institutions = []
// fetch(endpoint)
//     .then(res => res.json())
//     .then(data => institutions.push(...data.items))

// function findMatches(wordToMatch, institutions) {
//     return institutions.filter(org => {
//         const regex = new RegExp(wordToMatch, 'gi')
//         return org.name.match(regex)
//     })
// }

// function displayMatches() {
//     const matchArray = findMatches(this.value, institutions)
//     const html = matchArray.map(org => {
//         const regex = new RegExp(this.value, 'gi')
//         const orgName = org.name.replace(regex, `<span class="hl">${this.value}</span>`)
//         return `
//             <li onmouseover="getOrgName(this)">
//                 <span class="name">${orgName}</span>
//             </li>
//         `
//     }).join('')
//     suggestions.innerHTML = html
// }

// const searchInput = document.querySelector('.search')
// const suggestions = document.querySelector('.suggestions')

// searchInput.addEventListener('change', displayMatches);
// searchInput.addEventListener('keyup', displayMatches);

// function getOrgName(elem) {
//     // console.log(elem.innerText)
//     searchInput.value = elem.innerText
//     let ul = document.getElementById('institution-suggestions')
//     // console.log(searchInput)
// }