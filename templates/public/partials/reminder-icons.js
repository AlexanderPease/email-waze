var source   = $("#reminder-popover-content").html();
var template = Handlebars.compile(source);
$('.reminder-icon').each(function(){
  // Create or edit/delete
  if ($(this).hasClass('reminder-edit')) {
    var edit = true;
  } else {
    var edit = false;
  }
  // HTML
  var context = {
    profile_id: $(this).attr('data-profile-id'),
    reminder_id: $(this).attr('data-reminder-id'),
    edit: edit
  };
  var options = {
    'trigger': 'click',
    'placement': 'bottom',
    'html': true, 
    'content': template(context)
  }
  $(this).popover(options).parent().delegate('.reminder-option', 'click', function() {
    event.stopPropagation();
    // Checkbox, no action
    if ($(this).attr('data-reminder-recurring-checkbox')) {
      var checkbox = $(this).children('.recurring-checkbox').prop("checked");
    }
    // AJAX
    else {
      var profile_id = $(this).parent().parent().attr('data-profile-id'); // not proud
      var reminder_id = $(this).parent().parent().attr('data-reminder-id');
      // Delete reminder
      if ($(this).attr('data-reminder-delete')) {
        var url = "/api/reminder/" + reminder_id + "/delete";
        url += "?reminder_type=profile";
      }
      // Edit reminder
      else if (edit) {
        var url = "/api/reminder/" + reminder_id + "/edit?";
        url += "reminder_type=profile";
        url += "&days=" + $(this).attr('data-reminder-days');
        url += "&recurring=" + $(this).parent().find('.recurring-checkbox').prop("checked");
      }
      // Create new reminder
      else {
        var url = "/api/reminder/create?";
        url += "reminder_type=profile";
        url += "&doc_id=" + profile_id;
        url += "&days=" + $(this).attr('data-reminder-days');
        url += "&recurring=" + $(this).parent().find('.recurring-checkbox').prop("checked");
      }
      var options = {
        type: 'POST',
        url: url,
        success: function(response) {
          console.log(response);
          if (response['status_code'] == 200) {
            // Create/delete DOM elements if necessary
            var msg = response['data']['msg'];
            if (msg == 'create') {
              var reminderDisplay = '<span class="reminder-display" data-reminder-id=""></span></br>';
              // newly created reminders based on profile_id
              $('.reminder-icon[data-profile-id="' + profile_id + '"]').before(reminderDisplay);
            } else if (msg == 'delete') {

            }
            // Set both display
            var display_alert_type = response['data']['display_alert_type'];
            $('.reminder-display[data-profile-id="' + profile_id + '"]').text(display_alert_type);
            $('.reminder-display[data-reminder-id="' + reminder_id + '"]').text(display_alert_type);
            var display_action = response['data']['display_action'];
            $('.reminder-icon[data-profile-id="' + profile_id + '"]').text(display_action);
            $('.reminder-icon[data-reminder-id="' + reminder_id + '"]').text(display_action);  
          } else {
            $('.reminder-icon[data-profile-id="' + profile_id + '"]').text('Error! Try Again');
            $('.reminder-icon[data-reminder-id="' + reminder_id + '"]').text('Error! Try Again');
          }
        },
        error: function(response) {
          console.warn(response);
          $('.reminder-icon[data-profile-id="' + profile_id + '"]').text('Error! Try Again');
          $('.reminder-icon[data-reminder-id="' + reminder_id + '"]').text('Error! Try Again');
        }
      };
      console.log('Requesting: ' + options.url)
      $.ajax(options);
    }
  });
});