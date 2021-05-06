// On click of a community notification, update notification's viewed attribute to True
function markAsReadCommunity(elem) {
    let spanId = elem.id
    let splitString = spanId.split('_')
    let communityId = splitString[0]
    let notificationID = splitString[1]

    let url = `/notifications/community/read/${communityId}/${notificationID}`
    const method = 'POST'

    if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
        xhr=new XMLHttpRequest();

    } else {// code for IE6, IE5
        xhr=new ActiveXObject("Microsoft.XMLHTTP");
    }

    xhr.onreadystatechange=function(){
        if (xhr.readyState==4 && xhr.status==200){
            let label = document.getElementById(`notification-label-tag-${notificationID}`)
            label.classList.remove('orange-bg')
            label.classList.add('grey')
        }
        else if (xhr.status === 404) {  
            console.log("404 Not Found");
        }  
        else if (xhr.status === 403) {  
            console.log("403 Forbidden");
        }  
    }

    xhr.open(method, url)
    xhr.setRequestHeader("HTTP_X_REQUESTED_WITH","XMLHttpRequest")
    xhr.setRequestHeader("X-Requested-With","XMLHttpRequest")
    // const csrftoken = getCookie('csrftoken');
    // xhr.setRequestHeader('X-CSRF-Token', csrftoken)
    xhr.send()
}

function markAsReadInstitution(elem) {
    let spanId = elem.id
    let splitString = spanId.split('_')
    let institutionId = splitString[0]
    let notificationID = splitString[1]

    let url = `/notifications/institution/read/${institutionId}/${notificationID}`
    const method = 'POST'

    if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
        xhr=new XMLHttpRequest();

    } else {// code for IE6, IE5
        xhr=new ActiveXObject("Microsoft.XMLHTTP");
    }

    xhr.onreadystatechange=function(){
        if (xhr.readyState==4 && xhr.status==200){
            let label = document.getElementById(`notification-label-tag-${notificationID}`)
            label.classList.remove('orange-bg')
            label.classList.add('grey')
        }
        else if (xhr.status === 404) {  
            console.log("404 Not Found");
        }  
        else if (xhr.status === 403) {  
            console.log("403 Forbidden");
        }  
    }

    xhr.open(method, url)
    xhr.setRequestHeader("HTTP_X_REQUESTED_WITH","XMLHttpRequest")
    xhr.setRequestHeader("X-Requested-With","XMLHttpRequest")
    // const csrftoken = getCookie('csrftoken');
    // xhr.setRequestHeader('X-CSRF-Token', csrftoken)
    xhr.send()
}

function markAsReadResearcher(elem) {
    let spanId = elem.id
    let splitString = spanId.split('_')
    let researcherId = splitString[0]
    let notificationID = splitString[1]

    let url = `/notifications/researcher/read/${researcherId}/${notificationID}`
    const method = 'POST'

    if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
        xhr=new XMLHttpRequest();

    } else {// code for IE6, IE5
        xhr=new ActiveXObject("Microsoft.XMLHTTP");
    }

    xhr.onreadystatechange=function(){
        if (xhr.readyState==4 && xhr.status==200){
            let label = document.getElementById(`notification-label-tag-${notificationID}`)
            label.classList.remove('orange-bg')
            label.classList.add('grey')
        }
        else if (xhr.status === 404) {  
            console.log("404 Not Found");
        }  
        else if (xhr.status === 403) {  
            console.log("403 Forbidden");
        }  
    }

    xhr.open(method, url)
    xhr.setRequestHeader("HTTP_X_REQUESTED_WITH","XMLHttpRequest")
    xhr.setRequestHeader("X-Requested-With","XMLHttpRequest")
    // const csrftoken = getCookie('csrftoken');
    // xhr.setRequestHeader('X-CSRF-Token', csrftoken)
    xhr.send()
}

// KEEP: to find out the csrf token
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     console.log(cookieValue)
//     return cookieValue;
// }