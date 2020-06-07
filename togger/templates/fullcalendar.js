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
        // Set up our request
        request.open('POST', '/post_event');

        // Send our FormData object; HTTP headers are set automatically
        request.send(formData);

    };
    calendar = new FullCalendar.Calendar(calendarEl, {
        stickyHeaderDates: true,
        height: 'auto',
        scrollTime: "{{ settings.scrollTime }}",
        firstDay: "{{ settings.firstDay }}",
        slotMinTime: "{{ settings.slotMinTime }}",
        nextDayThreshold: "{{ settings.nextDayThreshold }}",
        slotMaxTime: "{{ settings.slotMaxTime }}",
        expandRows: true,
        headerToolbar: {
            left: isMobile() ? 'prev,next' : 'prev,next today',
            center: 'title',
            right: isMobile() ? 'dayGridMonth,timeGridDay,listWeek' : 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        {% if current_role().can_edit_events %}
        headerToolbar: {
            left: isMobile() ? 'prev,next' : 'prev,next today toggleEditButton',
            center: 'title',
            right: isMobile() ? 'dayGridMonth,timeGridDay,listWeek' : 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
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
        {% endif %}
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

        select: function(info) {
            url = '/render_event?startDateTime=' + info.start.toJSON() + '&endDateTime=' + info.end.toJSON() + '&allDay=' + info.allDay;
            renderModal(url);
        },

        eventClick: function(info) {
            var url;
            if (calendar.getOption("editable")){
                url = '/render_event?id=' + info.event.id;
            } else {
                url = '/render_shifts?id=' + info.event.id + '&isEditable=' + calendar.getOption("editable");
            }
            renderModal(url);
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
//    loadSettings()
    calendar.render();
    // https://stackoverflow.com/questions/61987141/dyanmic-change-text-on-custombuttons
    var editButton = document.getElementsByClassName("fc-toggleEditButton-button")
    if (editButton.length > 0){
        editButton[0].innerHTML = "edit"
    }

});
