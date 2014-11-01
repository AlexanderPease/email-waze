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
                var $div = $panel.find('div#rapporto');
                console.log($div)
                if (!$div.length)
                    $div = $('<div id="rapporto" style="position:relative;" />');
                $div.html(Mustache.render(html, contact));
                $panel.prepend($div);
                /*
                var src = lscache.get('p:'+ email);
                if (src) {
                    replace_image($div, src);
                } else {
                    first_valid_image(contact.images.sort(compare_images), function(src) {
                        if (!src)
                            src = 'chrome-extension://'+encodeURIComponent(ID)+'/img/profile.png';
                        lscache.set('p:'+contact.email, src);
                        replace_image($div, src);
                    });
                }
                */
            },
        });
    } else {
        console.log($panel);
    }
}


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
                var $div = $panel.find('div#rapporto');
                if (!$div.length)
                    $div = $('<div id="rapporto" style="position:relative;" />');
                $div.html(Mustache.render(html, connection));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}


function render_multiple_connections(connections_array) {
    console.log('render_multiple_connections()');
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        // Inject search bar on top...
        render_search()
        //...then append connections below
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/multiple_connections.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                console.log(connections_array);
                var $div = $panel.find('div#rapporto');
                if (!$div.length)
                    $div = $('<div id="rapporto" style="position:relative;" />');
                for (var i=0; i < connections_array.length; i++) {
                    console.log(connections_array[i]);
                    $div.append(Mustache.render(html, connections_array[i]));
                }
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
                var $div = $panel.find('div#rapporto');
                if (!$div.length)
                    $div = $('<div id="rapporto" style="position:relative;" />');
                $div.html(Mustache.render(html));
                $panel.prepend($div);
            },
        });
    } else {
        console.log($panel);
    }
}

/* Not sure what this does */
function find_account() {
    console.log('find_account()')
    var $email = $('div.gb_aa.gb_B').find('div.gb_ia');
    if ($email.length)
        console.log('find_account()');
        console.log($email.text());
        return $email.text();
    return undefined;
}


// Immediately render search form on page load
$(document).ready(function(){
    render_search()
});


// Lets content script listen for an search event triggered by local html
document.addEventListener("search", function(data) {
    console.log('Content script initiating search')
    var name = $('#search_name').val();
    var domain = $('#search_domain').val();
    chrome.extension.sendMessage({name:'get_connection_search', email:domain, name_string:name}, function(data) {
        if (data.data) {
            var connections = data.data;
            render_multiple_connections(connections);
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
            chrome.extension.sendMessage({name:'get_connection_by_email', email:email}, function(data) {
                if (data.data) {
                    var connection = data.data;
                    render_connection(connection);
                }
            });
            /*
            chrome.extension.sendMessage({name:'get_profile_by_email', email:email}, function(data) {
                if (data['profile']) {
                    var profile = data.profile;
                    console.log(profile)
                    render_profile(JSON.parse(profile));
                }
            });
            */
        }
    });
}


/* Get id of this chrome extension so render() can call local html files */
chrome.extension.sendMessage({name:'get_extension_id'}, function(id) {
    window.ID = id;
    start();
});
