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
    console.log($(this).attr('data-profile-id'))
    console.log($(this).attr('data-reminder-id'))
    console.log($(this))
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
          var msg = response['data']['msg'];
          $('.reminder-icon[data-profile-id="' + profile_id + '"]').text(msg);
          $('.reminder-icon[data-reminder-id="' + reminder_id + '"]').text(msg);
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