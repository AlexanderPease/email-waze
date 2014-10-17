console.log('content_script');

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

function render(contact) {
    console.log('render');
    var $panel = $('td.Bu.y3 div.nH.adC');
    if ($panel) {
        $.ajax({
            type: 'GET',
            url: 'chrome-extension://'+encodeURIComponent(ID)+'/templates/contact.html',
            cache: true,
            dataType: 'text',
            success: function(html) {
                var email_parts = contact.email.split('@');
                if (email_parts.length == 2) {
                    contact.email_name = email_parts[0];
                    contact.email_domain = email_parts[1];
                }
                var $div = $panel.find('div#rapporto');
                if (!$div.length)
                    $div = $('<div id="rapporto" style="position:relative;" />');
                contact.image_url_raw = 'chrome-extension://'+encodeURIComponent(ID)+'/img/ajax-loader.gif';
                $div.html(Mustache.render(html, contact));
                $panel.prepend($div);
                var src = lscache.get('p:'+contact.email);
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
            },
        });
    } else {
        console.log($panel);
    }
}

var PRIORITY = {
    'Gravatar': 1,
    'LinkedIn': 2,
    'Google+': 3,
    'Google Profile': 4,
    'Facebook': 5,
    'Twitter': 6,
    'AngelList': 7,
};

function compare_images(a, b) {
    var aa = PRIORITY[a['service']] || a;
    var bb = PRIORITY[b['service']] || b;
    if (aa < bb) return -1;
    if (aa > bb) return 1;
    return 0;
}

function first_valid_image(images, callback) {
    if (images.length > 0) {
        var el = new Image();
        var image = images.shift();
        var src = image.url;
        var success = function() {
            callback(src);
        }
        var fail = function() {
            first_valid_image(images, callback);
        }
        if (image['service'] && image.service.toLowerCase() == 'gravatar')
            src = src + '?s=80&d=404';
        el.onload = success;
        el.onerror = fail;
        el.src = src;
    } else {
        callback();
    }
}

function replace_image($div, src) {
    $div.find('img:first').attr('src', src);
}

function find_account() {
    var $email = $('div.gb_aa.gb_B').find('div.gb_ia');
    if ($email.length)
        return $email.text();
    return undefined;
}

function start() {
    console.log('start()');
    $(window).on('mouseover', function(e) {
        var $el = $(e.target);
        var email = email_from_attr($el) || email_from_mailto($el);
        if (email) {
            console.log(email);
            chrome.extension.sendMessage({name:'lookup_email', email:email, user:find_account()}, function(data) {
                console.log('callback');
                if (data['contact']) {
                    var contact = data.contact;
                    render(contact);
                }
            });
        }
    });
}

chrome.extension.sendMessage({name:'get_extension_id'}, function(id) {
    window.ID = id;
    start();
});
