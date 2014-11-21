function email_from_mailto($el) {
    if (!$el.attr('href'))
        return undefined;

    if ($el.attr('href').indexOf('mailto:') != 0)
        return undefined;

    var href = decodeURI($el.attr('href')).substring(7);
    if (!href)
        return undefined;

    return email_from_string(decodeURIComponent(href));
}


function email_from_attr($el) {
    if (!$el.attr('email'))
        return undefined;

    return $el.attr('email');
}


function email_from_string(str) {
    str = ' '+str+' ';
    var results = str.match(/\W(([^<>()[\]\\\/.=?&,;:\s@\"]+(\.[^<>()[\]\\\/.=?&,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))\W/g);
    if (results && results.length > 0) {
        for (var i=0; i < results.length; i++) {
            return $.trim(results[i].substr(1, results[i].length-2).toLowerCase());
        }
    }
    return undefined;
}


function render_profile(contact) {
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/profile.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                var email = contact.email;
                var email_parts = contact.email.split('@');
                if (email_parts.length == 2) {
                    contact.email_name = email_parts[0];
                    contact.email_domain = email_parts[1];
                }
                var $div = $panel.find('div#ansatz');
                console.log($div)
                if (!$div.length)
                    $div = $('<div id="ansatz" style="position:relative;" />');
                $div.html(Mustache.render(html, contact));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}


/* New layout for connection */
function render_connection(connection_dict) {
    console.log('render_connection()');
    console.log(connection_dict);
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        if (connection_dict.empty) {
            /* No connection */
            $.ajax({
                type: 'GET',
                url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/empty_connection.html',
                cache: true,
                dataType: 'text',
                success: function(html) {
                    var email = connection_dict.email;
                    var email_parts = email.split('@');
                    if (email_parts.length == 2) {
                        connection_dict.email_name = email_parts[0];
                        connection_dict.email_domain = email_parts[1];
                    }
                    var $div = $panel.find('div#ansatz');
                    if (!$div.length)
                        $div = $('<div id="ansatz" style="position:relative;" />');
                    $div.html(Mustache.render(html, connection_dict));
                    $panel.prepend($div);
                },
            });
        } else {
            /* There's a connection */
            $.ajax({
                type: 'GET',
                url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/connection.html',
                cache: true,
                dataType: 'text',
                success: function(html) {
                    // Email parts for display
                    var email = connection_dict.profile.email;
                    var email_parts = email.split('@');
                    if (email_parts.length == 2) {
                        connection_dict.email_name = email_parts[0];
                        connection_dict.email_domain = email_parts[1];
                    }

                    // Connection to self message
                    if (connection_dict.current_user) {
                        if (connection_dict.current_user.total_emails_out) {
                            connection_dict.current_user_msg = 'You last emailed on ' + connection_dict.current_user.latest_email_out_date;
                        } else {
                            connection_dict.current_user_msg = 'Last emailed you on ' + connection_dict.current_user.latest_email_in_date;
                        }
                    } else {
                        connection_dict.current_user_msg = "No email history with you";
                    }

                    // Team to profile connection to message
                    if (connection_dict.group_users_profile) {
                        if (connection_dict.group_users_profile.total_emails_out) {
                            connection_dict.group_users_profile_msg = connection_dict.group_users_profile.connected_user_email + ' last emailed on ' + connection_dict.group_users_profile.latest_email_out_date;
                        } else {
                            connection_dict.group_users_profile_msg = 'Last emailed ' + connection_dict.group_users_profile.connected_user_email + ' on ' + connection_dict.group_users_profile.latest_email_in_date;
                        }
                    } else {
                        connection_dict.group_users_profile_msg = "No email history with your teams";
                    }

                    // Team to domain connection to message
                    if (connection_dict.group_users_domain_generic) {
                        connection_dict.group_users_domain_msg = null;
                    } else {
                        if (connection_dict.group_users_domain) {
                            if (connection_dict.group_users_domain.total_emails_out) {
                                connection_dict.group_users_domain_msg = connection_dict.group_users_domain.connected_user_email + ' last emailed ' + connection_dict.group_users_domain.connected_profile_email + ' on ' + connection_dict.group_users_domain.latest_email_out_date;
                            } else {
                                connection_dict.group_users_domain_msg = connection_dict.group_users_domain.connected_profile_email + ' Last emailed ' + connection_dict.group_users_domain.connected_user_email + ' on ' + connection_dict.group_users_domain.latest_email_in_date;
                            }
                        } else {
                            connection_dict.group_users_domain_msg = "Your teams have no email history with " + connection_dict.email_domain;
                        }
                    }
                        

                    var $div = $panel.find('div#ansatz');
                    if (!$div.length)
                        $div = $('<div id="ansatz" style="position:relative;" />');
                    $div.html(Mustache.render(html, connection_dict));
                    $panel.prepend($div);
                },
            });
        }
    } else {
        console.log($panel);
    }
}


function render_multiple_connections(connections_array, url) {
    console.log('render_multiple_connections()');
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/multiple_connections.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                var total_num = connections_array.length;
                if (total_num < 5) {
                    var show_num = total_num;
                } 
                else {
                    var show_num = 5;
                    connections_array = connections_array.slice(0,show_num);
                }
                // Break out email handle vs. email domain for displaying
                for (var i=0; i < connections_array.length; i++) {
                    var email = connections_array[i].email;
                    var email_parts = email.split('@');
                    if (email_parts.length == 2) {
                        connections_array[i].email_name = email_parts[0];
                        connections_array[i].email_domain = email_parts[1];
                    }
                }
                // Insert into html
                var $div = $panel.find('div#ansatz');
                if (!$div.length)
                    $div = $('<div id="ansatz" style="position:relative;" />');
                
                var data = {
                    'connections': connections_array, 
                    'total_num': total_num,
                    'show_num': show_num,
                    'url': url
                }
                $div.html(Mustache.render(html, data));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}


function render_search() {
    console.log('render_search()');
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        // Get local html and inject into page
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/search.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                var $div = $panel.find('div#ansatz');
                if (!$div.length)
                    $div = $('<div id="ansatz" style="position:relative;" />');
                console.log('injecting search');
                $div.html(Mustache.render(html));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}

function render_login() {
    console.log('render_login()');
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        // Get local html and inject into page
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/login.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                var $div = $panel.find('div#ansatz');
                if (!$div.length)
                    $div = $('<div id="ansatz" style="position:relative;" />');
                console.log('injecting search');
                $div.html(Mustache.render(html));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}

function search_button_loading() {
    $('#search_button').attr('disabled', 'disabled').html("Loading...");
    setTimeout(function () {
        $('#search_button').removeAttr('disabled').html('Search');
    }, 3000);
}

$(document).ready(function(){
    // Bind event to detect whenever new URL loads
    $(window).on('hashchange', function(){
        console.log('Hash changed');
        var hash = window.location.hash;
        console.log(hash);
        if (hash.indexOf("compose=new") > -1){
            console.log("composing new message");
        } else {
            render_search();
        }
    });

    // Render search form on page load
    render_search();
});


// Content script listens for "search" event
document.addEventListener("search", function(data) {
    console.log('Content script initiating search')
    search_button_loading();
    var name = $('#search_name').val();
    var domain = $('#search_domain').val();
    chrome.extension.sendMessage({name:'get_connection_search', email:domain, name_string:name}, function(data) {
        if (data.data == 401 ){
            render_login();
        }
        else if (data.data) {
            var connections = data.data;
            var url = 'https://ansatz.me/search?name=' + name + '&domain=' + domain 
            render_multiple_connections(connections, url);
        } 
    });
})

// Content script listens for "rowClicked" event in multiple_connections.html
document.addEventListener("rowClicked", function(data) {
    console.log('Content script chose row')
    var email = $('#selected-domain').attr('profile-email');
    chrome.extension.sendMessage({name:'get_connection_by_email_for_extension', email:email}, function(data) {
        if (data.data == 401 ){
            render_login();
        }
        else if (data.data) {
            var connection_dict = data.data;
            render_connection(connection_dict);
        }
    });
})


/* Displays Connection for any email address that is moused over */
function start() {
    $(window).on('mouseover', function(e) {
        var $el = $(e.target);
        var email = email_from_attr($el) || email_from_mailto($el);
        if (email) {
            console.log('Mouse over ' + email);
            chrome.extension.sendMessage({name:'get_connection_by_email_for_extension', email:email}, function(data) {
                if (data.data == 401 ){
                    render_login();
                }
                else if (data.data) {
                    var connection_dict = data.data;
                    render_connection(connection_dict);
                }
            });
        }
    });
}


/* Get id of this chrome extension so render() can call local html files */
chrome.extension.sendMessage({name:'get_extension_id'}, function(id) {
    window.ID = id;
    start();
});

/* Not sure what this does 
function find_account() {
    console.log('find_account()')
    var $email = $('div.gb_aa.gb_B').find('div.gb_ia');
    if ($email.length)
        console.log('find_account()');
        console.log($email.text());
        return $email.text();
    return undefined;
}
*/

/* OLD
function render_connection(connection) {
    console.log('render_connection()');
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        // Get local html and inject into page
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/connection.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                var email = connection.email;
                var email_parts = email.split('@');
                if (email_parts.length == 2) {
                    connection.email_name = email_parts[0];
                    connection.email_domain = email_parts[1];
                }
                var $div = $panel.find('div#ansatz');
                if (!$div.length)
                    $div = $('<div id="ansatz" style="position:relative;" />');
                $div.html(Mustache.render(html, connection));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}
*/
