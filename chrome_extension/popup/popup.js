var ROOT_URL = 'http://ansatz.me/'

$(document).ready(function(){
  chrome.tabs.getSelected(null, function(tab) {
    var domain = get_domain(tab.url);
    $('#title').html('Searching for connections to "' + domain + '"');
    var options = {
      type: 'GET',
      url: ROOT_URL + 'api/domainconnections?domain=' + encodeURIComponent(domain),
      dataType: 'json',
      success: function(response) {
        console.log(response);
        var connectionset_list = response.data;
        var num_connections = connectionset_list.length;
        $('#title').html('You have ' + num_connections + 'connections to ' + domain);
      },
      error: function(response) {
        if (response.status_code == 401 || response.status_code == 500) {
          // User not logged in || couldn't find user in database
          var login_prompt = 'Please <a href="' + ROOT_URL
          login_prompt = '/auth/google" ' + 
            'target="_blank">log in</a> to use the Ansatz extension'
          $('#title').html(login_prompt);
        } else {
          var err = 'There was an error! Please try ' +
          '<a href="' + ROOT_URL + '">' + ROOT_URL + '</a> instead.'
          $('#title').html(err);
        }
      }
    };
    console.log('Requesting: ' + options.url)
    $.ajax(options);
  });
});


// Just splits out base url from href
function get_domain(url) {
  if (url.indexOf("http://") != -1) {
    url = url.split("http://")[1];
  }
  else if (url.indexOf("https://") != -1) {
    url = url.split("https://")[1];
  }
  if (url.indexOf("www.") != -1) {
    url = url.split("www.")[1];
  }
  if (url.indexOf("/") != -1) {
    url = url.split("/")[0];
  }
  return url;
}