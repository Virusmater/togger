var calendar;
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var postEvent = function(info) {
        if (info.event.extendedProps.recurId && !info.event.id) {
            var end = info.event.end
            if (end === null) {
                end = info.event.start;
            }
            renderModal('/render_recurrent?eventId=' + info.event.id + '&recurId=' + info.event.extendedProps.recurId +
                        '&start=' + info.event.start.toJSON() +
                        '&end=' + end.toJSON() + '&initStart=' + info.oldEvent.start.toJSON() +
                        '&timeZone=' + getTimeZone() + '&allDay=' + info.event.allDay +
                        '&eventTitle=' + info.event.title + '&description=' + info.event.extendedProps.description);
        } else {
            var request = new XMLHttpRequest();
            formData = new FormData();
            formData.append('start', info.event.start.toJSON());
            if (info.event.end) {
                formData.append('end', info.event.end.toJSON());
            } else {
                formData.append('end', info.event.start.toJSON());
            }
            formData.append('eventTitle', info.event.title);
            if (info.event.id) {
                formData.append('eventId', info.event.id);
            }
            if (info.event.extendedProps.recurId) {
                formData.append('recurId', info.event.extendedProps.recurId);
            }
            formData.append('initStart', info.oldEvent.start.toJSON());
            formData.append('initEnd', info.oldEvent.end.toJSON());
            formData.append('timeZone', getTimeZone());
            formData.append('allDay', info.event.allDay);
            formData.append('description', info.event.extendedProps.description);
            formData.append('csrf_token', '{{ csrf_token() }}');

            // Set up our request
            request.open('POST', '{{ url_for("event_api.post_event") }}');

            // Send our FormData object; HTTP headers are set automatically
            request.send(formData);
        }
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
        {% if current_role().has_role(50) %}
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
            url = '/render_event?start=' + info.start.toJSON() + '&end=' + info.end.toJSON()
                              + '&allDay=' + info.allDay + '&timeZone=' + getTimeZone();
            renderModal(url);
        },

        eventClick: function(info) {
            var end = info.event.end
            if (end === null) {
                end = info.event.start;
            }
            var url;
            if (calendar.getOption("editable")){
                if (info.event.id) {
                    url = '/render_event?id=' + info.event.id;
                } else {
                    url = '/render_event?recurId=' + info.event.extendedProps.recurId +
                                        '&start=' + info.event.start.toJSON() +
                                        '&end=' + end.toJSON() + '&timeZone=' + getTimeZone() +
                                        '&allDay=' + info.event.allDay;
                }
            } else {
                if (info.event.id) {
                    url = '/render_shifts?id=' + info.event.id + '&recurId=' + info.event.extendedProps.recurId +
                                        '&start=' + info.event.start.toJSON() + '&end=' + info.event.end.toJSON();
                } else {
                    url = '/render_shifts?recurId=' + info.event.extendedProps.recurId +
                                        '&start=' + info.event.start.toJSON() +
                                        '&end=' + end.toJSON() + '&allDay=' + info.event.allDay;
                }
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
        events: "{{ url_for('event_api.get_events') }}",
        eventColor: '#9F9C99',
        eventDidMount: function(info) {
          // Change color of dot marker
          var dotEl = info.el.getElementsByClassName('fc-daygrid-event-dot')[0];
          if (dotEl) {
            dotEl.style.borderColor = info.event.backgroundColor
          }

          // Change color of dot marker
          var dotEl2 = info.el.getElementsByClassName('fc-list-event-dot')[0];
          if (dotEl2) {
            dotEl2.style.borderColor = info.event.backgroundColor
          }
      }
    });
    calendar.render();
    // https://stackoverflow.com/questions/61987141/dyanmic-change-text-on-custombuttons
    var editButton = document.getElementsByClassName("fc-toggleEditButton-button")
    if (editButton.length > 0){
        editButton[0].innerHTML = "edit"
    }

});
