// On click of a community notification, update notification's viewed attribute to True
function markAsRead(elem) {
    let spanId = elem.id
    let splitString = spanId.split('_')
    let notificationID = splitString[1]

    let url = `/notifications/organization/read/${notificationID}`
    xhrRequestPost(url, notificationID)
}

function markAsReadUser(elem) {
    let spanId = elem.id
    let splitString = spanId.split('_')
    let notificationID = splitString[1]

    let url = `/notifications/read/${notificationID}/`
    xhrRequestPost(url, notificationID)
}

// Generic function for notifications
var xhrRequestPost = (url, notificationID) => {
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