$('.err').hide();
var name = CURRENT_MODAL.find('.name').val();
var invited_emails = CURRENT_MODAL.find('.invited_emails').val();
var domain_setting = CURRENT_MODAL.find('.domain_setting').val();
var group_id = CURRENT_MODAL.attr('group-id');
var this_btn = $(this);
// Client-side error checking
err_flag = false;
if (!name) {
  console.log(CURRENT_MODAL);
  CURRENT_MODAL.find('.err-name').text('Name cannot be blank!');
  CURRENT_MODAL.find('.err-name').show();
  err_flag = true;
}
if (!invited_emails && !domain_setting) {
  CURRENT_MODAL.find('.err-invited-emails').text('You either need to invite people or create a domain setting!');
  CURRENT_MODAL.find('.err-invited-emails').show();
  err_flag = true;
}
// Hit API if no client-side errors
if (!err_flag) {
  if (group_id) {
    var url = '/api/group/' + group_id + '/edit'
  } else {
    var url = '/api/group/create'
  }
  $(this).text('Creating...');
  $(this).attr('disabled', 'disabled');
  var options = {
    type: 'POST',
    url: url,
    data: {
      name: name, 
      invited_emails: invited_emails, 
      domain_setting: domain_setting
    },
    dataType: 'json',
    success: function(response) {
      console.log(response);
      if (response.status_code == 200) {
        this_btn.text('Success! Reloading page...')
        location.reload();
      } else {
        if (response.status_txt.indexOf('err-invited-emails') > -1) {
        CURRENT_MODAL.find('.err-invited-emails').text('Check your commas! Ensure email addresses make sense!');
        CURRENT_MODAL.find('.err-invited-emails').show();
        } 
        CURRENT_MODAL.find('.err-modal').show();
        this_btn.text('Save');
        this_btn.removeAttr('disabled');
      }
    },
    error: function(response) {
      console.warn(response);
      CURRENT_MODAL.find('.err-modal').show();
      this_btn.text('Create Team');
      this_btn.removeAttr('disabled');
    }
  };
  console.log('Requesting: ' + options.url)
  $.ajax(options);
} // if (!err_flag)