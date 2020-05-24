var calendar;
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var postEvent = function(info) {
        var request = new XMLHttpRequest();
        formData = new FormData();
        formData.append('startDateTime', info.event.start.toJSON())
        if (info.event.end) {
            formData.append('endDateTime', info.event.end.toJSON())
        } else {
            formData.append('endDateTime', info.event.start.toJSON())
        }
        formData.append('eventTitle', info.event.title)
        formData.append('eventId', info.event.id)
        formData.append('allDay', info.event.allDay)
        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                document.getElementById("modalContent").innerHTML = this.response
            }
        };
        // Set up our request
        request.open('POST', '/post_event');

        // Send our FormData object; HTTP headers are set automatically
        request.send(formData);

    };
    calendar = new FullCalendar.Calendar(calendarEl, {
        height: '100%',
        scrollTime: "16:00:00",
        firstDay: 1,
        slotMinTime: "09:00:00",
        nextDayThreshold: "09:00:00",
        slotMaxTime: "29:00:00",
        expandRows: true,
  customButtons: {
        toggleEditButton: {
        // https://stackoverflow.com/questions/61987141/dyanmic-change-text-on-custombuttons
        text: '',
              click: function() {
              if (calendar.getOption('editable')){
                calendar.setOption('editable',false)
                calendar.setOption('selectable',false)
                event.target.innerHTML = "edit"
              } else {
                calendar.setOption('editable',true)
                calendar.setOption('selectable',true)
                event.target.innerHTML = "stop"
              }
              }
            }}
         ,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        slotLabelFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        views: {
            listWeek: {
                titleFormat: isMobile() ? {
                    month: 'short',
                    day: '2-digit'
                } : {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                }
            },
            timeGridDay: {
                titleFormat: isMobile() ? {
                    month: 'short',
                    day: '2-digit'
                } : {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }
            }
        },
        headerToolbar: {
            left: isMobile() ? 'prev,next' : 'prev,next today toggleEditButton',
            center: 'title',
            right: isMobile() ? 'dayGridMonth,timeGridDay,listWeek' : 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },

        select: function(info) {
            var request = new XMLHttpRequest();
            request.open('GET', '/render_event?startDateTime=' + info.start.toJSON() + '&endDateTime=' + info.end.toJSON() + '&allDay=' + info.allDay, true);
            request.onload = function() {
                if (this.status >= 200 && this.status < 400) {
                    document.getElementById("modalContent").innerHTML = this.response
                    $("#modal").modal()
                }
            };
            request.send();
        },

        eventClick: function(info) {
            var request = new XMLHttpRequest();
            request.open('GET', '/render_shifts?id=' + info.event.id + '&isEditable=' + calendar.getOption("editable"), true);
            request.onload = function() {
                if (this.status >= 200 && this.status < 400) {
                    document.getElementById("modalContent").innerHTML = this.response
                    $("#modal").modal()
                }
            };
            request.send();
        },

        eventResize: postEvent,
        eventDrop: postEvent,
        initialView: isMobile() ? 'timeGridDay' : 'timeGridWeek',
        navLinks: true, // can click day/week names to navigate views
        editable: false,
        selectable: false,
        nowIndicator: true,
        dayMaxEvents: true, // allow "more" link when too many events
        events: '/get_events',
        eventColor: '#9F9C99'
    });

    calendar.render();
    // https://stackoverflow.com/questions/61987141/dyanmic-change-text-on-custombuttons
    document.getElementsByClassName("fc-toggleEditButton-button")[0].innerHTML = "edit"

});
