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
        if (connectionset_list == null) {
          $('#title').html('You have no connections to ' + domain);
        } else {
          var num_connections = connectionset_list.length;
          var tbody_html = "<thead><tr><th>Name</th><th>Email</th><th>Connections</th></tr></thead>"
          tbody_html = tbody_html + "<tbody>"
          for (var i=0; i<num_connections; i++) {
            connectionset = connectionset_list[i]
            tbody_html = tbody_html + "<tr><td>" + 
              connectionset['name'] + "</td><td>" + '<a href="mailto:' +
              connectionset['email'] + '">' + 
              connectionset['email'] + "</a></td><td>"
            for (var j=0; j<connectionset['connections'].length; j++) {
              tbody_html = tbody_html + 
                connectionset['connections'][j]['connected_user_name'] + " (" +
                connectionset['connections'][j]['connected_user_email'] + ")</br>"
            }
            tbody_html = tbody_html + "</td></tr>"
          }
          tbody_html = tbody_html + "</tbody>"
          title_html = 'Showing all ' + num_connections + ' connections to ' 
            + domain + '</br><a href="' + ROOT_URL + 'search?domain=' +
            domain + '" target="_blank">' + 'Click here</a> for more info'
          $('#title').html(title_html);
          $('#table-body').html(tbody_html);
        }
      }, //success
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