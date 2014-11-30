var ROOT_URL = 'http://ansatz.me/'

$(document).ready(function(){
  chrome.tabs.getSelected(null, function(tab) {
    var domain = get_domain(tab.url);
    $('#title').text('Searching for connections to "' + domain + '"');
    var options = {
      type: 'GET',
      url: ROOT_URL + 'api/test',
      dataType: 'json',
      success: function(response) {
        console.log(response);
      },
      error: function(response) {
        console.warn(response);
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