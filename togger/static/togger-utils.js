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