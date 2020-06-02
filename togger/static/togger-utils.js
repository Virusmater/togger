function submit_modal(form, modal, action) {
        var request = new XMLHttpRequest();
        formData  = new FormData(form);
        request.onload = function() {
        if (this.status >= 200 && this.status < 400) {
            $(modal).modal('hide')
            calendar.refetchEvents()
        }
        };
        // Set up our request
        if (action == "postEvent") {
            url = '/post_event'
        } else if (action == "postShifts") {
url = '/post_shifts'

        } else if (action == "removeEvent") {
url = '/remove_event'

        }
        request.open( 'POST', url );
        // Send our FormData object; HTTP headers are set automatically
        request.send( formData );
        }

function isMobile(){
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
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