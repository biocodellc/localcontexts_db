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

// Researchers : add project/notice
function noticeToggle(img) {
    let imgID = img.id
    let hiddenInupt = document.getElementById('which-notice')
    let bcNotice = document.getElementById('bc-notice-img')
    let tkNotice = document.getElementById('tk-notice-img')
    let p = document.getElementById('notice-text')

    let bcText = 'The BC Notice serves as a visible notification that there is accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The BC Notice recognizes the rights of Indigenous peoples to permission the use of information, collections, data and digital sequence information generated from the biodiversity or genetic resources associated with traditional lands, waters, and territories. The BC Notice may indicate that BC (Biocultural) Labels are in development and their implementation is being negotiated.'
    let tkText = 'The TK Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The TK Notice may indicate that TK Labels are in development and their implementation is being negotiated.'

    if (imgID == bcNotice.id) {
        tkNotice.classList.add('opacity-4')
        bcNotice.classList.remove('opacity-4')
        p.innerText = bcText
        hiddenInupt.value = 'bc_notice'
    } else {
        bcNotice.classList.add('opacity-4')
        tkNotice.classList.remove('opacity-4')
        p.innerText = tkText
        hiddenInupt.value = 'tk_notice'
    }
}

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

function expandTKLabel(img) {
    let labelContainer = document.getElementById('expand-tklabels')
    let fullCard = document.getElementById('collapsed-tkcard')
    let info = document.getElementById('tklabel-info')
    console.log(img.id)

    if (info.style.height == "0px") {
        labelContainer.style.height = "auto"
        info.style.height = "auto"
        fullCard.style.height = "auto"
    } else {
        labelContainer.style.height = "auto"
        info.style.height = "0px"
        fullCard.style.height = "auto"
    }

    let targetImg = img.id
    let title = document.getElementById('tk-label-title')
    let templateText = document.getElementById('label-template-text-tk')
    let whyUseLabelText = document.getElementById('why-use-this-label-tk')

    switch (targetImg) {
        case 'tka':
            // whichImgClicked('tka')
            title.textContent = tkAttributionName
            templateText.textContent = tkAttributionText
            whyUseLabelText.textContent = tkAttribution
            break;
        case 'tkcl':
            // whichImgClicked('tkcl')
            title.textContent = tkClanName
            templateText.textContent = tkClanText
            whyUseLabelText.textContent = tkClanUse
            break;
        case 'tkf':
            // whichImgClicked('tkf')
            title.textContent = tkFamilyName
            templateText.textContent = tkFamilyText
            whyUseLabelText.textContent = tkFamilyUse
            break;
        case 'tkmc':
            // whichImgClicked('tkmc')
            title.textContent = tkMultipleCommunityName
            templateText.textContent = tkMultipleCommunityText
            whyUseLabelText.textContent = tkMultipleCommunityUse
            break;
        case 'tko':
            // whichImgClicked('tko')
            title.textContent = tkOutreachName
            templateText.textContent = tkOutreachText
            whyUseLabelText.textContent = tkOutreachUse
            break;
        case 'tknv':
            // whichImgClicked('tknv')
            title.textContent = tkNonVerifiedName
            templateText.textContent = tkNonVerifiedText
            whyUseLabelText.textContent = tkNonVerifiedUse
            break;
        case 'tkv':
            // whichImgClicked('tkv')
            title.textContent = tkVerifiedName
            templateText.textContent = tkVerifiedText
            whyUseLabelText.textContent = tkVerifiedUse
            break;
        case 'tknc':
            // whichImgClicked('tknc')
            title.textContent = tkNonCommercialName
            templateText.textContent = tkNonCommercialText
            whyUseLabelText.textContent = tkNonCommercialUse
            break;
        case 'tkc':
            // whichImgClicked('tkc')
            title.textContent = tkCommercialName
            templateText.textContent = tkCommercialText
            whyUseLabelText.textContent = tkCommercialUse
            break;
        case 'tkcs':
            // whichImgClicked('tkcs')
            title.textContent = tkCulturallySensitiveName
            templateText.textContent = tkCulturallySensitiveText
            whyUseLabelText.textContent = tkCulturallySensitiveUse
            break;
        case 'tkco':
            // whichImgClicked('tkco')
            title.textContent = tkCommunityUseOnlyName
            templateText.textContent = tkCommunityUseOnlyText
            whyUseLabelText.textContent = tkCommunityUseOnlyUse
            break;
        case 'tks':
            // whichImgClicked('tks')
            title.textContent = tkSeasonalName
            templateText.textContent = tkSeasonalText
            whyUseLabelText.textContent = tkSeasonalUse
            break;
        case 'tkwg':
            // whichImgClicked('tkmg')
            title.textContent = tkWomenGeneralName
            templateText.textContent = tkWomenGeneralText
            whyUseLabelText.textContent = tkWomenGeneralUse
            break;
        case 'tkmg':
            // whichImgClicked('tkmg')
            title.textContent = tkMenGeneralName
            templateText.textContent = tkMenGeneralText
            whyUseLabelText.textContent = tkMenGeneralUse
            break;
        case 'tkmr':
            // whichImgClicked('tkmr')
            title.textContent = tkMenRestrictedName
            templateText.textContent = tkMenRestrictedText
            whyUseLabelText.textContent = tkMenRestrictedUse
            break;
        case 'tkwr':
            // whichImgClicked('tkwr')
            title.textContent = tkWomenRestrictedName
            templateText.textContent = tkWomenRestrictedText
            whyUseLabelText.textContent = tkWomenRestrictedUse
            break;
        case 'tkss':
            // whichImgClicked('tkss')
            title.textContent = tkSecretSacredName
            templateText.textContent = tkSecretSacredText
            whyUseLabelText.textContent = tkSecretSacredUse
            break;
    }

}
