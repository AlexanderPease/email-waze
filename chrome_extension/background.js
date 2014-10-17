console.log('background.js');

var LOGIN_URL = 'https://rapportive.com/login_status';
var LOOKUP_URL = 'https://profiles.rapportive.com/contacts/email/';
var API_HOST = '104.131.218.68';
var API_URL = 'http://'+API_HOST+'/api/profiles';
var API_ERROR_URL = 'http://'+API_HOST+'/api/errors';

var VERSION = chrome.app.getDetails().version;
var ID = chrome.app.getDetails().id;

var Queue = $.Deferred().resolve();

// setup messaging
chrome.extension.onMessage.addListener(function(request, sender, callback) {
    if (window[request.name] !== undefined) {
        var after = function() {
            return window[request.name].call(this, request, callback, sender);
        };
        Queue = Queue.then(after, after);
        return true;
    }
});

function get_session(user, email, callback, force) {
    if (lscache.get('session') && lscache.get('session')['session_token'] && !force) {
        callback(lscache.get('session'));
    } else {
        var url = LOGIN_URL;
        if (user)
            url = url+'?user_email='+encodeURIComponent(user);
        else
            url = url+'?user_email='+encodeURIComponent(email);
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            success: function(data) {
                if (data.status == 200 && data['session_token']) {
                    lscache.set('session', {'session_token': data['session_token']});
                    callback(lscache.get('session'));
                } else {
                    console.warn(data);
                    lscache.remove('session')
                    save_error(email, data.status, data);
                }
            },
            error: function(response) {
                console.warn(response);
                lscache.remove('session')
                save_error(email, response.status, response.responseText);
            },
        });
    }
}

function lookup_email(data, callback) {
    console.log('lookup_email');
    if (lscache.get('e:'+data.email)) {
        callback({contact:lscache.get('e:'+data.email)});
    } else {
        if (lscache.get('sleep')) {
            lscache.remove('sleep');
            setTimeout(function() { lookup_email(data, callback); }, 3000);
        } else {
            lscache.set('sleep', true);
            get_session(data.user, data.email, function(session) {
                var options = {
                    type: 'GET',
                    url: LOOKUP_URL+encodeURIComponent(data.email),
                    dataType: 'json',
                    headers: {
                        'X-Session-Token': session.session_token,
                    },
                    success: function(response) {
                        lscache.remove('sleep');
                        save_response(response);
                        lscache.set('e:'+data.email, response.contact);
                        if (is_ok(response)) {
                            callback({contact:response.contact});
                        }
                    },
                    error: function(response) {
                        console.warn(response);
                        lscache.remove('session')
                        save_error(data.email, response.status, response.responseText);
                    },
                };
                $.ajax(options);
            });
        }
    }
    return true;
}

function is_ok(data) {
    return data['status'] && data.status >= 200 && data.status < 300 && data['success'] != 'nothing_useful';
}

function save_error(email, status, text) {
    $.ajax({
        type: 'POST',
        url: API_ERROR_URL,
        data: {
            email: email,
            response_status: status,
            response_text: text,
        },
    });
}

function save_response(data) {
    $.ajax({
        type: 'POST',
        url: API_URL,
        data: {
            data: JSON.stringify(data),
        },
    });
}

function get_extension_id(data, callback) {
    callback(ID);
}
