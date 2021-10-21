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

// BC Content
var provenanceName = 'BC Provenance (BC P)'
var multipleCommunityName = 'BC Multiple Communities (BC MC)'
var openToCollabName = 'BC Open to Collaboration (BC CB)'
var openToCommercializationName = ' BC Open to Commercialization (BC C)'
var researchUseName = 'BC Research Use (BC R)'
var consentVerifiedName = 'BC Consent Verified (BC CV)'
var consentNonVerifiedName = 'BC Consent Non-Verified (BC CNV)'
var clanName = 'BC Clan (BC CL)'
var outreachName = 'BC Outreach (BC O)'
var nonCommercialName = 'BC Non-Commercial (BC NC)'

var provenanceUse = 'Indigenous peoples have the right to make decisions about the future use of information, biological collections, data and digital sequence information (DSI) that derives from associated lands, waters and territories. This Label supports the practice of proper and appropriate acknowledgement into the future.'
var multipleCommUse = 'This Label should be used to indicate that multiple communities have responsibility, custodianship and/or ownership over the geographic regions where this species or biological entity originates/is found. This Label recognizes that whilst one community might exert specific authority, other communities also have rights and responsibilities for use and care.'
var openToCollabUse = 'This Label is being used to indicate that the community is open to research collaborations and outreach activities. With this Label, future opportunities for collaboration and engagement are supported.'
var openToCommUse = 'Indigenous peoples have the right to benefit from information, biological collections, data and digital sequence information (DSI) that derives from traditional lands, waters and territories. This Label is being used to indicate the express interest that [community name or authorizing party] has in being a primary party to any future negotiations if future commercialization opportunities arise from these resources.'
var researchUse = 'This label should be used for permissioning the use of information, collections, data and digital sequence information for unspecified research. The research use label does not give permission for commercialization activities.'
var consentVerifiedUse = 'Indigenous peoples have the right to permission the use of information, biological collections, data and digital sequence information (DSI) that derives from associated lands, waters and territories. This Label verifies that there are consent conditions in place for uses of information, collections, data and digital sequence information.'
var consentNonVerifiedUse = 'The consent associated with this data has not been verified by the community. Reasons for this could include that it has not been appropriately vetted, has mistakes, omissions, lack of informed consent, or its process of creation was through research which did not follow proper community protocols.'
var clanUse = 'This Label should be used when you would like external users to know that this material is subject to conditions for circulation relating to clan membership and/or is according to protocols for clan relationships. Because these conditions have not historically been recognized, this Label helps make these conditions for use and circulation clearer. Specifically, the Label asks future users to respect culturally specific rules of use and to make informed decisions about using this type of material.'
var outreachUse = 'This Label should be used when you would only like your biocultural materials and/or data used for educational outreach activities. Outreach activities means to share works outside the community in order to increase and raise awareness and education about your family, clan and/or community. Sites for outreach activities can include schools, universities, libraries, archives, museums, online forums, and small learning groups.'
var nonCommercialUse = 'This Label should be used when you would like to let external users who have access to your biocultural data know that it should only be used in non-commercial ways. You are asking users to be respectful with your data and ask that it not be used to derive economic benefits or used in any way that makes it into a commodity for sale or purchase.'

var provenanceText = 'This Label is being used to affirm an inherent interest Indigenous people have in the scientific collections and data about communities, peoples, and the biodiversity found within traditional lands, waters and territories. [Community name or authorizing party] has permissioned the use of this collection and associated data for research purposes, and retains the right to be named and associated with it into the future. This association reflects a significant relationship and responsibility to [the species or biological entity] and associated scientific collections and data.'
var multipleCommunityText = 'This Label is being used to affirm responsibility and ownership over this information, collection, data and digital sequence information is spread across several distinct communities. Use will be dependent upon discussion and negotiation with multiple communities.'
var openToCollabText = 'This Label is being used to make clear [community name or authorizing body] is open to future engagement, collaboration, and partnership around research and outreach opportunities.'
var openToCommercializationText = 'This Label is being used to indicate that [community name or authorizing party] is open to commercialization opportunities that might derive from any information, collections, data and digital sequence information (DSI) to which this Label is connected. As a primary party in any partnership and collaboration opportunities that emerge from the use of these resources, we retain an express interest in any future negotiations.'
var researchUseText = 'This Label is being used by [community name or authorizing body] to allow this information, collection, data and digital sequence information to be used for unspecified research purposes. This Label does not provide permission for commercialization activities.  [Optional return of research results statement].'
var consentVerifiedText = 'This Label is being used to verify that [community name or authorizing party] have consent conditions in place for the use of this information, collections, data and digital sequence information.'
var consentNonVerifiedText = 'This Label is being used because there are concerns about the accuracy of the consent and/or representations made for this data. This material was not created through informed consent or community protocols for research and engagement.'
var clanText = 'This Label is being used to indicate that this material is traditionally and usually not publicly available. The Label lets future users know that this data has specific conditions for use and sharing because of clan membership and/or relationships. This Label asks viewers of this data to respect the cultural values and expectations about circulation and use defined by designated clans, members, and their internal relations.'
var outreachText = 'The Label is letting any users know that this data can be used for educational outreach activities. This Label asks you to respect the designated circulation conditions for these biocultural materials and/or data and additionally, where possible, to develop a means for fair and equitable reciprocal exchange for the use of this data with the relevant BC holders.'
var nonCommercialText = 'This Label is being used to indicate that these biocultural materials and/or data have been designated as being available for non-commercial use. You are allowed to use this material for non-commercial purposes including for research, study, or public presentation and/or online in blogs or non-commercial websites. This Label asks you to think and act with respect and responsibility towards this data and the original custodians.'


// TK Content
var tkAttributionName = 'TK Attribution (TK A)'
var tkClanName = 'TK Clan (TK CL)'
var tkFamilyName = 'TK Family (TK F)'
var tkMultipleCommunityName = 'TK Multiple Communities (TK MC)'
var tkOutreachName = 'TK Outreach (TK O)'
var tkNonVerifiedName = 'TK Non-Verified (TK NV)'
var tkVerifiedName = 'TK Verified (TK V)'
var tkNonCommercialName = 'TK Non-Commercial (TK NC)'
var tkCommercialName = 'TK Open to Commercialization (TK OC)'
var tkCulturallySensitiveName = 'TK Culturally Sensitive (TK CS)'
var tkCommunityVoiceName = 'TK Community Voice (TK CV)'
var tkCommunityUseOnlyName = 'TK Community Use Only (TK CO)'
var tkSeasonalName = 'TK Seasonal (TK S)'
var tkWomenGeneralName = 'TK Women General (TK WG)'
var tkMenGeneralName = 'TK Men General (TK MG)'
var tkMenRestrictedName = 'TK Men Restricted (TK MR)'
var tkWomenRestrictedName = 'TK Women Restricted (TK WR)'
var tkSecretSacredName = 'TK Secret / Sacred (TK SS)'
var tkOpenToCollaborationName = 'TK Open to Collaboration (TK CB)'
var tkCreativeName = 'TK Creative (TK CR)'

var tkAttributionUse = 'This label should be used when you would like anyone who uses this material to know who the correct sources, custodians, owners are. This is especially useful if this material has been wrongly attributed or important names of the people involved in making this material or safeguarding this material, are missing. This label allows you to correct historical mistakes in terms of naming and acknowledging the legitimate authorities for this material. This label asks for future users to also apply the correct names and attribution.'
var tkClanUse = 'This Label should be used when you would like external users to know that this material is subject to conditions for circulation relating to clan membership and or is according to protocols for clan relationships. Because these conditions have not historically been recognized, this Label helps make these conditions for use and circulation clearer. Specifically, the Label asks future users to respect culturally specific rules of use and to make informed decisions about using this type of material.'
var tkFamilyUse = 'This label should be used when you would like external users to know that this material is subject to certain conditions for circulation. This material is usually only shared between family members. Because these conditions have not historically been recognized, this label helps make these conditions clearer for future users. Specifically it asks them to respect culturally specific rules of use and to make different and fair decisions about using this type of material.'
var tkMultipleCommunityUse = 'This label should be used to indicate that multiple communities have responsibilities of custodianship and/or ownership over specific material. This label recognizes that no singular community has explicit control. Rather, rights and responsibilities for use are spread across communities through already existing community protocols and ongoing cultural relationships.'
var tkOutreachUse = 'This label should be used when you would only like your cultural materials used for educational outreach activities. Outreach activities means to share works outside the community in order to increase and raise awareness and education about your family, clan and/or community. Sites for outreach activities can include schools, universities, libraries, archives, museums, online forums and small learning groups. Depending on what kind of context and the possibilities for increased circulation of this material, this label helps TK holders and users to develop new possibilities in the fair and equitable reciprocal exchange for use of this material in outreach activities. This exchange might include access to educational or other resources that your community has difficulty accessing under other circumstances.'
var tkNonVerifiedUse = 'This material has not been verified by the community. Reasons for this could include that it has not been appropriately vetted, has mistakes, omissions, derogatory language, lack of informed consent, or its process of creation was through dishonest research which did not follow proper community protocols.'
var tkVerifiedUse = 'This label should be used when you and your community are satisfied with the way in which your traditional knowledge materials are being represented online or offline. This label affirms that appropriate conditions for access and use are in place and that whoever has made this material accessible has made accommodations for cultural protocols associated with the knowledge. It lets users know that the right thing is being done by your community protocols and standards.'
var tkNonCommercialUse = 'This label should be used when you would like to let external users who have access to your material know that it should only be used in non-commercial ways. You are asking users to be respectful and fair with your cultural materials and ask that it not be used to derive economic benefits or used in any way that makes it into a commodity for sale or purchase.'
var tkOpenToCommercializationUse = 'Communities have the right to benefit commercially from the information that is derived from their traditional knowledge. This Label is being used to indicate an expressed interest in being a primary party to any future negotiations if commercialization opportunities arise.'
var tkCulturallySensitiveUse = 'This Label should be used when you would like external users to know that this material has special sensitivities around it and should be treated with great care. These sensitivities could include: that it has only recently been reconnected with the community from which it originates, that the community is currently vetting and spending time with the material, and/or that the material is culturally valued and needs to be kept safe. This Label could also be used to indicate that there are cultural sensitivities around this material arising from legacies of colonialism, for instance, the use of derogatory language or descriptive errors within the content and/or content descriptions.'
var tkCommunityVoiceUse = 'This Label should be used when you would like to encourage community members to share their knowledge, stories and experiences. This Label would usually be used within a community-based archive to encourage the sharing of stories. This Label indicates that the current narrative or explanation that accompanies this material is incomplete or partial and that many community voices are needed to help make sense and understand the event, photograph, recording or heritage item. The Community Voice Label encourages multiplicity in the telling, listening and sharing of community histories and cultural knowledge.'
var tkCommunityUseOnlyUse = 'This label should be used when you would like external users to know that this material is subject to certain conditions of circulation namely that this material is usually not circulated beyond the family, clan or community. Because these conditions have not historically been recognized, this label helps make these conditions clearer for future users. Specifically it asks them to respect culturally specific rules of use and to make different and fair decisions about using this type of material.'
var tkSeasonalUse = 'This label should be used when you want to let external users know that the material that is openly circulating has seasonal conditions of access and use. This could mean that some material should only be used and heard at particular times of the year. It could also mean that the environment and land where this material derives also influences and impacts its meaning and significance. This label can be used to help external users know that there are land-based teachings in this material which affect proper use and respectful understanding.'
var tkWomenGeneralUse = 'This label should be used when you want to let external users know that the material circulating should only be shared between women in the community. This is a women’s general label and indicates that there are restrictions of access and use to women within the community based on customary law. This label can be used to help external users recognize that with this material there are specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge can only be shared among specific members of the community. It should be used to complement already existing customs and protocols of access and use.'
var tkMenGeneralUse = 'This label should be used when you want to let external users know that the material circulating should only be shared between men in the community. This is a men’s general label and indicates that there are restrictions of access and use to men based on customary law. This label can be used to help external users recognize that with this material there are specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge can only be shared among specific members of the community. It should be used to complement already existing customs and protocols of access and use.'
var tkMenRestrictedUse = 'This label should be used when you want to let external users know that the material circulating freely is actually of a highly restricted nature. This is a men’s highly restricted label and indicates that there are restrictions of access and use based on customary law. This label can be used to help external users recognize that with this material there are very specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge expressions can only be shared among specific members of the community. Only authorized [and/or initiated] men within the community should be using this material.'
var tkWomenRestrictedUse = 'This label should be used when you want to let external users know that the material circulating freely is actually of a highly restricted nature. This is a women’s highly restricted label and indicates that there are restrictions of access and use based on customary law. This label can be used to help external users recognize that with this material there are very specific protocols and conditions of use. This label is designed to recognize that some knowledge is gendered, and that certain knowledge expressions can only be shared among specific members of the community. Only authorized [and/or initiated] women within the community should be using this material.'
var tkSecretSacredUse = 'This label should be used when you want to let external users know that the material that is openly circulating contains secret/sacred information and that it has specific conditions of access and use. These conditions potentially include restrictions upon access. Using this label helps to alert external users that this material is special and requires respectful and careful treatment. It asks users to make different decisions about using it and, importantly, to discuss any potential use with you.'
var tkOpenToCollaborationUse = 'This Label is being used to indicate that the community is open to research collaborations. With this Label, future opportunities for collaboration and engagement are supported.'
var tkCreativeUse = 'This Label should be used when an individual artist or author would like to clearly connect creative practices with traditional knowledge deriving from their own community. While an individual artist or author has standard copyright and creative commons licenses available to use, this Label helps make clear that a creative practice is also deeply connected to a collective responsibility around the use and sharing of traditional knowledge.'

var tkAttributionText = 'This label is being used to correct historical mistakes or exclusions pertaining to this material. This is especially in relation to the names of the people involved in performing or making this work and/or correctly naming the community from which it originally derives. As a user you are being asked to also apply the correct attribution in any future use of this work.'
var tkClanText = 'This Label is being used to indicate that this material is traditionally and usually not publicly available. The Label lets future users know that this material has specific conditions for use and sharing because of clan membership and/or relationships. This material is not, and never was, free, public and available for everyone. This Label asks viewers of these materials to respect the cultural values and expectations about circulation and use defined by designated clans, members and their internal relations.'
var tkFamilyText = 'This label is being used to indicate that this material is traditionally and usually not publicly available. The label is correcting a misunderstanding about the circulation options for this material and letting any users know that this material has specific conditions for sharing between family members. Who these family members are, and how sharing occurs will be defined in each locale. This material is not, and never was, free, public and available for everyone at anytime. This label asks you to think about how you are going to use this material and to respect different cultural values and expectations about circulation and use.'
var tkMultipleCommunityText = 'Responsibility and ownership over this material is spread across several distinct communities. Use will be dependent upon discussion and negotiation with the multiple communities named herein [insert names]. Decisions about use will need to be decided collectively. As an external user of this material you are asked to recognize and respect cultural protocols in relation to the use of this material and clear your intended use with the relevant communities.'
var tkOutreachText = 'This label is being used to indicate that this material is traditionally and usually not publicly available. The label is correcting a misunderstanding about the circulation options for this material and letting any users know that this material can be used for educational outreach activities. This label asks you to respect the designated circulation conditions for this material and additionally, where possible, to develop a means for fair and equitable reciprocal exchange for the use of this material with the relevant TK holders. This exchange might include access to educational or other resources that are difficult to access under normal circumstances.'
var tkNonVerifiedText = 'This Label is being used because there are concerns about accuracy and/or representations made in this material. This material was not created through informed consent or community protocols for research and engagement. Therefore questions about its accuracy and who/how it represents this community are being raised.'
var tkVerifiedText = 'This label affirms that the representation and presentation of this material is in keeping with community expectations and cultural protocols. It lets you know that for the individual, family or community represented in this material, use is considered fair, reasonable and respectful.'
var tkNonCommercialText = 'This material has been designated as being available for non-commercial use. You are allowed to use this material for non-commercial purposes including for research, study or public presentation and/or online in blogs or non-commercial websites. This label asks you to think and act with fairness and responsibility towards this material and the original custodians.'
var tkOpenToCommercializationText = 'This Label is being used to indicate that [community name or authorized party] is open to commercialization opportunities that might derive from any cultural material with traditional knowledge to which this Label is connected to. As a primary party for any partnership and collaboration opportunities that emerge from the use of this cultural material and traditional knowledge, we retain an expressed interest in any future negotiations.'
var tkCulturallySensitiveText = 'This Label is being used to indicate that this material has cultural and/or historical sensitivities. The label asks for care to be taken when this material is accessed, used, and circulated, especially when materials are first returned or reunited with communities of origin. In some instances, this label will indicate that there are specific permissions for use of this material required directly from the community itself.'
var tkCommunityVoiceText = 'This Label is being used to encourage the sharing of stories and voices about this material. The Label indicates that existing knowledge or descriptions are incomplete or partial. Any community member is invited and welcome to contribute to our community knowledge about this event, photograph, recording or heritage item. Sharing our voices helps us reclaim our histories and knowledge. This sharing is an internal process.'
var tkCommunityUseOnlyText = 'This label is being used to indicate that this material is traditionally and usually not publicly available. The label is correcting a misunderstanding about the circulation options for this material and letting any users know that this material has specific conditions for circulation within the community. It is not, and never was, free, public and available for everyone at anytime. This label asks you to think about how you are going to use this material and to respect different cultural values and expectations about circulation and use.'
var tkSeasonalText = 'This label is being used to indicate that this material traditionally and usually is heard and/or utilized at a particular time of year and in response to specific seasonal changes and conditions. For instance, many important ceremonies are held at very specific times of the year. This label is being used to indicate sophisticated relationships between land and knowledge creation. It is also being used to highlight the relationships between recorded material and the specific contexts where it derives, especially the interconnected and embodied teachings that it conveys.'
var tkWomenGeneralText = 'This material has specific gender restrictions on access. It is usually only to be accessed and used by women in the community. If you are not from the community and you have accessed this material, you are requested not to download, copy, remix or otherwise circulate this material to others without permission. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkMenGeneralText = 'This material has specific gender restrictions on access. It is usually only to be accessed and used by men in the community. If you are not from the community and you have accessed this material, you are requested to not download, copy, remix or otherwise circulate this material to others without permission. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkMenRestrictedText = 'This material has specific gender restrictions on access. It is regarded as important secret and/or ceremonial material that has community-based laws in relation to who can access it. Given its nature it is only to be accessed and used by authorized [and initiated] men in the community. If you are an external third party user and you have accessed this material, you are requested to not download, copy, remix or otherwise circulate this material to others. This material is not freely available within the community and it therefore should not be considered freely available outside the community. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkWomenRestrictedText = 'This material has specific gender restrictions on access. It is regarded as important secret and/or ceremonial material that has community-based laws in relation to who can access it. Given its nature it is only to be accessed and used by authorized [and initiated] women in the community. If you are an external third party user and you have accessed this material, you are requested to not download, copy, remix or otherwise circulate this material to others. This material is not freely available within the community and it therefore should not be considered freely available outside the community. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkSecretSacredText = 'This label is being used to indicate that this material is traditionally and usually not publicly available because it contains important secret or sacred components. The label is correcting a misunderstanding about the significance of this material and therefore its circulation conditions. It is letting users know that because of its secret/sacred status it is not, and was never free, public and available for everyone at anytime. This label asks you to think about whether you should be using this material and to respect different cultural values and expectations about circulation and use.'
var tkOpenToCollaborationText = 'This Label is being used to make clear [community name or authorizing body] is open to future engagement, collaboration, and partnership around research opportunities.'
var tkCreativeText = 'This Label is being used to acknowledge the relationship between the creative practices of [name] and [community name] and the associated cultural responsibilities.'

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


    // Set content based on which Label was selected

    switch (targetImg) {
        // Protocols
        case 'bccv':
            openBCInfoDiv(infoProt)
            whichBCImgClicked('bccv')
            titleProt.textContent = consentVerifiedName
            templateTextProt.textContent = consentVerifiedText
            whyUseLabelTextProt.textContent = consentVerifiedUse
            break;
        case 'bccnv':
            openBCInfoDiv(infoProt)
            whichBCImgClicked('bccnv')
            titleProt.textContent = consentNonVerifiedName
            templateTextProt.textContent = consentNonVerifiedText
            whyUseLabelTextProt.textContent = consentNonVerifiedUse
            break;

        // Provenance
        case 'bcmc':
            openBCInfoDiv(infoProv)
            whichBCImgClicked('bcmc')
            titleProv.textContent = multipleCommunityName
            templateTextProv.textContent = multipleCommunityText
            whyUseLabelTextProv.textContent = multipleCommUse
            break;
        case 'bcp':
            openBCInfoDiv(infoProv)
            whichBCImgClicked('bcp')
            titleProv.textContent = provenanceName
            templateTextProv.textContent = provenanceText
            whyUseLabelTextProv.textContent = provenanceUse
            break;
        case 'bccl':
            openBCInfoDiv(infoProv)
            whichBCImgClicked('bccl')
            titleProv.textContent = clanName
            templateTextProv.textContent = clanText
            whyUseLabelTextProv.textContent = clanUse
            break;

        // Permissions
        case 'bcr':
            openBCInfoDiv(infoPerms)
            whichBCImgClicked('bcr')
            titlePerms.textContent = researchUseName
            templateTextPerms.textContent = researchUseText
            whyUseLabelTextPerms.textContent = researchUse
            break;
        case 'bco':
            openBCInfoDiv(infoPerms)
            whichBCImgClicked('bco')
            titlePerms.textContent = outreachName
            templateTextPerms.textContent = outreachText
            whyUseLabelTextPerms.textContent = outreachUse
            break;
        case 'bcnc':
            openBCInfoDiv(infoPerms)
            whichBCImgClicked('bcnc')
            titlePerms.textContent = nonCommercialName
            templateTextPerms.textContent = nonCommercialText
            whyUseLabelTextPerms.textContent = nonCommercialUse
            break;
        case 'bcoc':
            openBCInfoDiv(infoPerms)
            whichBCImgClicked('bcoc')
            titlePerms.textContent = openToCommercializationName
            templateTextPerms.textContent = openToCommercializationText
            whyUseLabelTextPerms.textContent = openToCommUse
            break;
        case 'bccb':
            openBCInfoDiv(infoPerms)
            whichBCImgClicked('bccb')
            titlePerms.textContent = openToCollabName
            templateTextPerms.textContent = openToCollabText
            whyUseLabelTextPerms.textContent = openToCollabUse
            break;
    }

}

//  Assign input value based on which bc label image is selected in Community: select-labels
function whichBCImgClicked(val) {
    var inputProv = document.getElementById('bc-label-value-type-prov')
    var inputProt = document.getElementById('bc-label-value-type-prot')
    var inputPerms = document.getElementById('bc-label-value-type-perm')

    if (val == 'bcp' || val == 'bcmc' || val == 'bccl')  {
        inputProv.value = val
    } else if (val == 'bccv' || val == 'bccnv') {
        inputProt.value = val
    } else if (val == 'bcr' || val == 'bccb' || val == 'bcoc' || val == 'bco' || val == 'bcnc') {
        inputPerms.value = val
    }
    displayExpandedImage(val)
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

// Assign input value based on which bc label image is selected in Community: select-labels
function whichTKImgClicked(val) {
    var inputProv = document.getElementById('tk-label-value-type-prov')
    var inputProt = document.getElementById('tk-label-value-type-prot')
    var inputPerms = document.getElementById('tk-label-value-type-perms')

    if(val == 'tka' || val == 'tkcl' || val == 'tkf' || val == 'tkmc' || val == 'tkcv' || val == 'tkcr') {
        inputProv.value = val
    } else if (val == 'tkv' || val == 'tknv' || val == 'tks' || val == 'tkwg' || val == 'tkmg' || val == 'tkmr' || val == 'tkwr' || val == 'tkcs' || val == 'tkss') {
        inputProt.value = val
    } else if (val == 'tkoc' || val == 'tknc' || val == 'tkco' || val == 'tko' || val == 'tkcb') {
        inputPerms.value = val
    }

    displayExpandedImage(val)
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

    switch (id) {
        case 'bcr':
            whyUseText.textContent = researchUse
            hiddenInput.value = researchUseName
            templateText.textContent = researchUseText
            break;
        case 'bccv':
            whyUseText.textContent = consentVerifiedUse
            hiddenInput.value = consentVerifiedName
            templateText.textContent = consentVerifiedText
            break;
        case 'bcoc':
            whyUseText.textContent = openToCommUse
            hiddenInput.value = openToCommercializationName
            templateText.textContent = openToCommercializationText
            break;
        case 'bccb':
            whyUseText.textContent = openToCollabUse
            hiddenInput.value = openToCollabName
            templateText.textContent = openToCollabText
            break;
        case 'bcmc':
            whyUseText.textContent = multipleCommUse
            hiddenInput.value = multipleCommunityName
            templateText.textContent = multipleCommunityText
            break;
        case 'bcp':
            whyUseText.textContent = provenanceUse
            hiddenInput.value = provenanceName
            templateText.textContent = provenanceText
            break;

        case 'bccl':
            whyUseText.textContent = clanUse
            hiddenInput.value = clanName
            templateText.textContent = clanText
            break;
        case 'bco':
            whyUseText.textContent = outreachUse
            hiddenInput.value = outreachName
            templateText.textContent = outreachText
            break;
        case 'bccnv':
            whyUseText.textContent = consentNonVerifiedUse
            hiddenInput.value = consentNonVerifiedName
            templateText.textContent = consentNonVerifiedText
            break;
        case 'bcnc':
            whyUseText.textContent = nonCommercialUse
            hiddenInput.value = nonCommercialName
            templateText.textContent = nonCommercialText
            break;
                                                            
        case 'tka':
            whyUseText.textContent = tkAttributionUse
            hiddenInput.value = tkAttributionName
            templateText.textContent = tkAttributionText
            break;
        case 'tkcl':
            whyUseText.textContent = tkClanUse
            hiddenInput.value = tkClanName
            templateText.textContent = tkClanText
            break;
        case 'tkf':
            whyUseText.textContent = tkFamilyUse
            hiddenInput.value = tkFamilyName
            templateText.textContent = tkFamilyText
            break;
        case 'tkmc':
            whyUseText.textContent = tkMultipleCommunityUse
            hiddenInput.value = tkMultipleCommunityName
            templateText.textContent = tkMultipleCommunityText
            break;
        case 'tko':
            whyUseText.textContent = tkOutreachUse
            hiddenInput.value = tkOutreachName
            templateText.textContent = tkOutreachText
            break;
        case 'tknv':
            whyUseText.textContent = tkNonVerifiedUse
            hiddenInput.value = tkNonVerifiedName
            templateText.textContent = tkNonVerifiedText
            break;
        case 'tkv':
            whyUseText.textContent = tkVerifiedUse
            hiddenInput.value = tkVerifiedName
            templateText.textContent = tkVerifiedText
            break;
        case 'tknc':
            whyUseText.textContent = tkNonCommercialUse
            hiddenInput.value = tkNonCommercialName
            templateText.textContent = tkNonCommercialText
            break;
        case 'tkoc':
            whyUseText.textContent = tkOpenToCommercializationUse
            hiddenInput.value = tkCommercialName
            templateText.textContent = tkOpenToCommercializationText
            break;
        case 'tkcs':
            whyUseText.textContent = tkCulturallySensitiveUse
            hiddenInput.value = tkCulturallySensitiveName
            templateText.textContent = tkCulturallySensitiveText
            break;
        case 'tkcv':
            whyUseText.textContent = tkCommunityVoiceUse
            hiddenInput.value = tkCommunityVoiceName
            templateText.textContent = tkCommunityVoiceText
            break;
        case 'tkco':
            whyUseText.textContent = tkCommunityUseOnlyUse
            hiddenInput.value = tkCommunityUseOnlyName
            templateText.textContent = tkCommunityUseOnlyText
            break;
        case 'tks':
            whyUseText.textContent = tkSeasonalUse
            hiddenInput.value = tkSeasonalName
            templateText.textContent = tkSeasonalText
            break;
        case 'tkwg':
            whyUseText.textContent = tkWomenGeneralUse
            hiddenInput.value = tkWomenGeneralName
            templateText.textContent = tkWomenGeneralText
            break;
        case 'tkmg':
            whyUseText.textContent = tkMenGeneralUse
            hiddenInput.value = tkMenGeneralName
            templateText.textContent = tkMenGeneralText
            break;
        case 'tkmr':
            whyUseText.textContent = tkMenRestrictedUse
            hiddenInput.value = tkMenRestrictedName
            templateText.textContent = tkMenRestrictedText
            break;
        case 'tkwr':
            whyUseText.textContent = tkWomenRestrictedUse
            hiddenInput.value = tkWomenRestrictedName
            templateText.textContent = tkWomenRestrictedText
            break;
        case 'tkss':
            whyUseText.textContent = tkSecretSacredUse
            hiddenInput.value = tkSecretSacredName
            templateText.textContent = tkSecretSacredText
            break;
        case 'tkcb':
            whyUseText.textContent = tkOpenToCollaborationUse
            hiddenInput.value = tkOpenToCollaborationName
            templateText.textContent = tkOpenToCollaborationText
            break;
        case 'tkcr':
            whyUseText.textContent = tkCreativeUse
            hiddenInput.value = tkCreativeName
            templateText.textContent = tkCreativeText
            break;
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
        case 'tkcv':
            openInfoDiv(infoProv)
            whichTKImgClicked('tkcv')
            titleProv.textContent = tkCommunityVoiceName
            templateTextProv.textContent = tkCommunityVoiceText
            whyUseLabelTextProv.textContent = tkCommunityVoiceUse
            break;

        // Protocols Labels
        case 'tknv':
            openInfoDiv(infoProt)
            whichTKImgClicked('tknv')
            titleProt.textContent = tkNonVerifiedName
            templateTextProt.textContent = tkNonVerifiedText
            whyUseLabelTextProt.textContent = tkNonVerifiedUse
            break;
        case 'tkv':
            openInfoDiv(infoProt)
            whichTKImgClicked('tkv')
            titleProt.textContent = tkVerifiedName
            templateTextProt.textContent = tkVerifiedText
            whyUseLabelTextProt.textContent = tkVerifiedUse
            break;
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
        case 'tknc':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tknc')
            titlePerms.textContent = tkNonCommercialName
            templateTextPerms.textContent = tkNonCommercialText
            whyUseLabelTextPerms.textContent = tkNonCommercialUse
            break;
        case 'tkoc':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkoc')
            titlePerms.textContent = tkCommercialName
            templateTextPerms.textContent = tkOpenToCommercializationText
            whyUseLabelTextPerms.textContent = tkOpenToCommercializationUse
            break;
        case 'tkco':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkco')
            titlePerms.textContent = tkCommunityUseOnlyName
            templateTextPerms.textContent = tkCommunityUseOnlyText
            whyUseLabelTextPerms.textContent = tkCommunityUseOnlyUse
            break;
        case 'tkcb':
            openInfoDiv(infoPerms)
            whichTKImgClicked('tkcb')
            titlePerms.textContent = tkOpenToCollaborationName
            templateTextPerms.textContent = tkOpenToCollaborationText
            whyUseLabelTextPerms.textContent = tkOpenToCollaborationUse
            break;
        case 'tkcr':
            openInfoDiv(infoProv)
            whichTKImgClicked('tkcr')
            titleProv.textContent = tkCreativeName
            templateTextProv.textContent = tkCreativeText
            whyUseLabelTextProv.textContent = tkCreativeUse
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
    console.log(projectIdInput)
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


var inputList = document.getElementById('selectedOrganizationInputList')

if (inputList) {
    inputList.addEventListener('change', setCommunity)
    inputList.addEventListener('click', setCommunity)
}

function setCommunity() {
    let hiddenCommunityInput = document.getElementById('hidden-target-input')
    hiddenCommunityInput.value = inputList.value
}

var joinBtn = document.getElementById('openJoinRequestModalBtn')
if (joinBtn) {
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
var createResearcherBtn = document.getElementById('submitResearcher')
if (createResearcherBtn) {
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

