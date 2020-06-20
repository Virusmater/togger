function submit_modal(form, modal, url, method) {
    if (form.checkValidity() == false) {
        return;
    }
    if(typeof method === "undefined")
        {method = 'POST';}
    var request = new XMLHttpRequest();
    formData = new FormData(form);
    request.onload = function() {
        if (this.status >= 200 && this.status < 400) {
            $(modal).modal('hide')
            calendar.refetchEvents()
        } else {
            document
                .getElementById("modalContent")
                .innerHTML = this.response
        }
    };
    request.open(method, url);
    // Send our FormData object; HTTP headers are set automatically
    request.send(formData);
}

function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator
        .userAgent
    )
}

function loadSettings() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            settings = JSON.parse(this.responseText)
            for (let [key, value] of Object.entries(settings)) {
                calendar.setOption(`${key}`, `${value}`);
            }
        }
    };
    xhttp.open("GET", "/get_settings", true);
    xhttp.send();
}

function renderModal(url) {
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = function() {
        if (this.status >= 200 && this.status < 400) {
            document
                .getElementById("modalContent")
                .innerHTML = this.response
            $("#modal").modal()
        }
    };
    request.send();
}


function newShare(form, modal, url) {
    var request = new XMLHttpRequest();
    formData = new FormData(form);
    request.onload = function() {
        if (this.status >= 200 && this.status < 400) {
            document.getElementById('roleName').style.display = "none";
            document.getElementById('buttonCopyShare').style.display = "initial"
            document.getElementById("shareUrl").value = this.response;
        }
    };
    request.open('POST', url);
    // Send our FormData object; HTTP headers are set automatically
    request.send(formData);
}

function copyText(inputField) {
    /* Select the text field */
    inputField.select();
    inputField.setSelectionRange(0, 99999); /*For mobile devices*/
    /* Copy the text inside the text field */
    document.execCommand("copy");
}

function changeShare(form, url) {
    var request = new XMLHttpRequest();
    formData = new FormData(form);
    request.open('PUT', url);
    // Send our FormData object; HTTP headers are set automatically
    request.send(formData);
}

function signMyself(firstName, lastName) {
    document
        .getElementById("newName")
        .value = firstName + " " + lastName
}

function getTimeZone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
}

if (
    !
    isMobile()) {
    $(document).on('shown.bs.modal', function(e) {
        $('[autofocus]', e.target).focus();
    });
}


$(document).on('shown.bs.modal', function(e) {
    $('[data-toggle="popover"]').popover()
});