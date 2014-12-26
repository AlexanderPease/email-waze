App = Ember.Application.create({});

App.Router.map(function() {
  this.resource('search');
  this.resource('about');
  this.resource('admin');
    
  this.resource('posts', function() {
    this.resource('post', { path: ':post_id' });
  });
});

App.Router.reopen({
  location: 'history'
});

// Debugger helper
Handlebars.registerHelper("debug", function(optionalValue) {
  console.log("Current Context");
  console.log("====================");
  console.log(this);
 
  if (optionalValue) {
    console.log("Value");
    console.log("====================");
    console.log(optionalValue);
  }
});

/*******************************************************************************
Index
*******************************************************************************/
App.IndexRoute = Ember.Route.extend({
  model: function(params) {
    Ember.Logger.log('Loading current user info...');
    return Ember.$.getJSON('/app').then(function(resp){
      console.log(resp);
      return resp.data;
    });
  }
});

App.IndexController = Ember.ObjectController.extend({
  actions: {  
    searchSubmit: function() {
      Ember.Logger.log('Search button submitted...');
      var name = this.get('nameField');
      var domain = this.get('domainField');
      var search_url = '/search?name=' + name + '&domain=' + domain;
      this.transitionToRoute(search_url);
    }
  }
});

App.IndexView = Ember.View.extend({
  didInsertElement: function() {
    $(window).resize(function () {
      fixFooter();
      fixSearchBg();
    });

    var fixSearchBg = function() {
    //fixes gradient background div height for search results page
      if ($('.search-background.js-stretch-height').length && $(window).innerWidth() > 767) {
        var padTop = parseInt($('.search-background').css('padding-top').split('px')[0]);
        var padBottom = parseInt($('.search-background').css('padding-bottom').split('px')[0]);
        $('.search-background').height($(window).innerHeight() - $('.nav').height() - $('footer').height() - padTop - padBottom);
      }
    }
    $(document).ready(function() {
      fixSearchBg();
    });


    //{% block user_welcome_js %}{% end %}
  }
});



Ember.Handlebars.helper('casual_name', function(user) {
  /*
  Returns casual name for User instance
  */
  if (user.given_name && user.given_name != ""){
    return user.given_name
  } else {
    return user.name
  }
});


/*******************************************************************************
Search
*******************************************************************************/
App.SearchController = Ember.ObjectController.extend({
  queryParams: ['name', 'domain'],
  name: null,
  domain: null,
  
  nameField: Ember.computed.oneWay('name'),
  domainField: Ember.computed.oneWay('domain'),
  actions: {  
    searchSubmit: function() {
      Ember.Logger.log('Search button submitted...');
      this.set('name', this.get('nameField'));
      this.set('domain', this.get('domainField'));
    }
  },
  popover: function (profile) {
  /*
  Writes popover body html for all connections for a single profile
  */
  console.log("in popoverHtml func");
  var p = profile;
  console.log(profile)
  var html = "<h3>Connection to " + p.name + "</h3>";
  for (i=0; i<p.connections.length; i++) {
    var c = p.connections[i];
    if (i > 0) {
      html += "</br>"
    }
    if (c.total_emails_out == 0 && c.total_emails_in == 0) {
      html += c.connected_user_email + " <--> " + p.email + ":</br>";
    } else {
      html += c.connected_user_email + " --> " + p.email + ": ";
      if (c.total_emails_out == 0) {
        html += "0 emails"
      } else if (c.total_emails_out == 1) {
        html += c.total_emails_out + " email, most recently on " + c.latest_email_out_date;
      } else {
        html += c.total_emails_out + " emails, most recently on " + c.latest_email_out_date;
      }
      html += "</br>";
      html += p.email + " --> " + c.connected_user_email + ": ";
      if (c.total_emails_in == 0) {
        html += "0 emails"
      } else if (c.total_emails_in == 1) {
        html += c.total_emails_in + " email, most recently on " + c.latest_email_in_date;
      } else {
        html += c.total_emails_in + " emails, most recently on " + c.latest_email_in_date;
      }
      html += "</br>";
    }
  }
  console.log(html);
  return html;
  }.property('popover')
});


App.SearchRoute = Ember.Route.extend({
  queryParams: {
    name: {
      refreshModel: true
    },
    domain: {
      refreshModel: true 
    }
  },
  model: function(params) {
    var name = params.name;
    var domain = params.domain;
    var url = '/app/search?name=' + name + '&domain=' + domain
    Ember.Logger.log('Loading search model from: ' + url);
    return {"group_connection_set": [{"name": "Albert Wenger", "connections": [{"total_emails_out": 4115, "connected_user_email": "albert@usv.com", "total_emails_in": 4893, "connected_user_name": "Albert Wenger", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/05", "latest_email_out_date": "2014/11/05"}], "email": "albert@usv.com"}, {"name": "Joel Monegro", "connections": [{"total_emails_out": 171, "connected_user_email": "joel@usv.com", "total_emails_in": 158, "connected_user_name": "Joel Monegro", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/04", "latest_email_out_date": "2014/11/04"}], "email": "joel@usv.com"}, {"name": "Jonathan Libov", "connections": [{"total_emails_out": 124, "connected_user_email": "jonathan@usv.com", "total_emails_in": 113, "connected_user_name": "Jonathan Libov", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/04", "latest_email_out_date": "2014/11/04"}], "email": "jonathan@usv.com"}, {"name": "Brittany Laughlin", "connections": [{"total_emails_out": 492, "connected_user_email": "brittany@usv.com", "total_emails_in": 539, "connected_user_name": "Brittany Laughlin", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/06", "latest_email_out_date": "2014/11/04"}], "email": "brittany@usv.com"}, {"name": "Alexander Pease", "connections": [{"total_emails_out": 859, "connected_user_email": "alexander@usv.com", "total_emails_in": 1116, "connected_user_name": "Alexander Pease", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/03", "latest_email_out_date": "2014/11/03"}], "email": "alexander@usv.com"}, {"name": "Alexander Pease", "connections": [{"total_emails_out": 2, "connected_user_email": "me@alexanderpease.com", "total_emails_in": 2, "connected_user_name": "Alexander Pease", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2013/09/10", "latest_email_out_date": "2013/09/10"}], "email": "me@alexanderpease.com"}], "profiles": [{"name": "Fred Wilson", "burner": "fredwilson", "connections": [{"total_emails_out": 4115, "connected_user_email": "albert@usv.com", "total_emails_in": 4893, "connected_user_name": "Albert Wenger", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/05", "latest_email_out_date": "2014/11/05"}, {"total_emails_out": 171, "connected_user_email": "joel@usv.com", "total_emails_in": 158, "connected_user_name": "Joel Monegro", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/04", "latest_email_out_date": "2014/11/04"}, {"total_emails_out": 124, "connected_user_email": "jonathan@usv.com", "total_emails_in": 113, "connected_user_name": "Jonathan Libov", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/04", "latest_email_out_date": "2014/11/04"}, {"total_emails_out": 492, "connected_user_email": "brittany@usv.com", "total_emails_in": 539, "connected_user_name": "Brittany Laughlin", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/06", "latest_email_out_date": "2014/11/04"}, {"total_emails_out": 859, "connected_user_email": "alexander@usv.com", "total_emails_in": 1116, "connected_user_name": "Alexander Pease", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/03", "latest_email_out_date": "2014/11/03"}, {"total_emails_out": 2, "connected_user_email": "me@alexanderpease.com", "total_emails_in": 2, "connected_user_name": "Alexander Pease", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2013/09/10", "latest_email_out_date": "2013/09/10"}], "email": "fred@usv.com"}], "profile_connection_set": [{"name": "Fred Wilson", "connections": [{"total_emails_out": 4115, "connected_user_email": "albert@usv.com", "total_emails_in": 4893, "connected_user_name": "Albert Wenger", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/05", "latest_email_out_date": "2014/11/05"}, {"total_emails_out": 171, "connected_user_email": "joel@usv.com", "total_emails_in": 158, "connected_user_name": "Joel Monegro", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/04", "latest_email_out_date": "2014/11/04"}, {"total_emails_out": 124, "connected_user_email": "jonathan@usv.com", "total_emails_in": 113, "connected_user_name": "Jonathan Libov", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/04", "latest_email_out_date": "2014/11/04"}, {"total_emails_out": 492, "connected_user_email": "brittany@usv.com", "total_emails_in": 539, "connected_user_name": "Brittany Laughlin", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/06", "latest_email_out_date": "2014/11/04"}, {"total_emails_out": 859, "connected_user_email": "alexander@usv.com", "total_emails_in": 1116, "connected_user_name": "Alexander Pease", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2014/11/03", "latest_email_out_date": "2014/11/03"}, {"total_emails_out": 2, "connected_user_email": "me@alexanderpease.com", "total_emails_in": 2, "connected_user_name": "Alexander Pease", "connected_profile_name": "Fred Wilson", "connected_profile_email": "fred@usv.com", "latest_email_in_date": "2013/09/10", "latest_email_out_date": "2013/09/10"}], "email": "fred@usv.com"}]}

    return Ember.$.getJSON(url).then(function(resp){
      // TODO: handle no results

      console.log(resp);
      return resp.data;
    });
  },
  /*actions: {
    refresh: function() {
      Ember.Logger.log('Route is now refreshing...');
      this.refresh();
    }
  },*/
  /* breaking the model for some reason
  setupController: function(controller) {
    // Set the IndexController's `title`
    controller.set('title', "Ansatz - Search");
    //controller.set('domain', 'bullshit');
    //console.log(controller);
  }
  */
});

App.SearchView = Ember.View.extend({
  didInsertElement: function() {
    $(document).ready(function(){
      // Results message
      queryParameters = getQueryParameters()
      var terms = "";
      var firstParam = true;
      for (var k in queryParameters) {
        if (k != 'page') {
          if (queryParameters[k]) {
            if (!firstParam) {
              terms = terms + ", " // Comma-delimitation after first parameter listed
            }
            terms = terms + '"' + queryParameters[k] + '"';
            firstParam = false;
          }
        }
      }
      $('#results').text('Results for ' + terms);

      // Popovers for each results row
      $('body').popover({
        placement: "top",
        trigger: "focus",
        selector: "tr[id=popover-row]",
        container: "body",
        html: true,
        template: '<div class="popover popover-medium"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
      });

      /* Load new page when pagination is clicked */
      $('.page-link').click(function(){
        queryParameters = getQueryParameters();
         
        // Add new parameters or update existing ones
        var pageNum = $(this).attr('data-page-number');
        var currentPageNum = parseInt(getQueryParameters['page']);
        if (pageNum == 'prev') {
          if (currentPageNum) {
            queryParameters['page'] = currentPageNum - 1;
          } else {
            // If there is no currentPageNum, then it's on page 1
            queryParameters['page'] = 2
          }
        } else if (pageNum == 'next' ) {
          if (currentPageNum) {
            queryParameters['page'] = currentPageNum + 1;
          } else {
            // If there is no currentPageNum, then it's on page 1
            queryParameters['page'] = 2
          }
        }
        else {
          queryParameters['page'] = pageNum;
        }
         
        /*
         * Replace the query portion of the URL.
         * jQuery.param() -> create a serialized representation of an array or
         *     object, suitable for use in a URL query string or Ajax request.
         */
        location.search = $.param(queryParameters); // Causes page to reload
      });

    });//ready
    function getQueryParameters() {
       /* queryParameters -> handles the query string parameters
       * queryString -> the query string without the fist '?' character
       * re -> the regular expression
       * m -> holds the string matching the regular expression */
      var queryParameters = {}, queryString = location.search.substring(1), re = /([^&=]+)=([^&]*)/g, m;
      // Creates a map with the query string parameters
      while (m = re.exec(queryString)) {
          queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
      }
      return queryParameters
    }
  }
});


App.SearchBarSmallComponent = Ember.Component.extend({
  searchfoo: function() {
    console.log('clicked');
  }
});


Ember.Handlebars.helper('display_num_connections', function(profile) {
  /*
  Ex: "2 connections" or "1 connection" or "N/A"
  */
  if (profile.connections.length == 1) {
    return "1 Connection"
  } else if (profile.connections.length == 0) {
    return "N/A"
  } else{
    return profile.connections.length + " Connections"
  }
});

Ember.Handlebars.helper('connections_popover', function(profile) {
  /*
  Writes popover body html for all connections for a single profile
  */
  console.log('entered connections popover');
  var p = profile;
  var html = "<h3>Connection to " + p.name + "</h3>";
  for (i=0; i<p.connections.length; i++) {
    var c = p.connections[i];
    if (i > 0) {
      html += "</br>"
    }
    if (c.total_emails_out == 0 && c.total_emails_in == 0) {
      html += c.connected_user_email + " <--> " + p.email + ":</br>";
    } else {
      html += c.connected_user_email + " --> " + p.email + ": ";
      if (c.total_emails_out == 0) {
        html += "0 emails"
      } else if (c.total_emails_out == 1) {
        html += c.total_emails_out + " email, most recently on " + c.latest_email_out_date;
      } else {
        html += c.total_emails_out + " emails, most recently on " + c.latest_email_out_date;
      }
      html += "</br>";
      html += p.email + " --> " + c.connected_user_email + ": ";
      if (c.total_emails_in == 0) {
        html += "0 emails"
      } else if (c.total_emails_in == 1) {
        html += c.total_emails_in + " email, most recently on " + c.latest_email_in_date;
      } else {
        html += c.total_emails_in + " emails, most recently on " + c.latest_email_in_date;
      }
      html += "</br>";
    }
  }
  return html;
});

/*******************************************************************************
Admin
*******************************************************************************/
App.AdminRoute = Ember.Route.extend({
  model: function() {
    return Ember.$.getJSON('/app/admin').then(function(resp){
      console.log(resp);
      return resp.data;
    });
  }
});


Ember.Handlebars.helper('truncate', function(string) {
  /*
  Truncates long strings and adds ellipses at end
  */
  var MAX_LENGTH = 40;
  if (string.length > MAX_LENGTH) {
    string = string.substring(0, MAX_LENGTH);
    string = string + "...";
  }
  return string;
});

Ember.Handlebars.helper('domain', function(string) {
  /*
  Returns just the domain name of self.email
  Ex: reply.craigslist.com from foo@reply.craigslist.com
  */
  return string.split('@')[1]
});

Ember.Handlebars.helper('unity', function(integer) {
  /*
  Returns True if integer is 1, False if not
  */
  return integer == 1;
});

/*******************************************************************************
Posts example code
*******************************************************************************/

App.PostsRoute = Ember.Route.extend({
  model: function() {
    return Ember.$.getJSON('http://tomdale.net/api/get_recent_posts/?callback=?').then(function(data){
      console.log(data);
      return data.posts.map(function(post){
        post.body = post.content;
        console.log(post);
        return post;
      });
    });
  }
});

App.PostRoute = Ember.Route.extend({
  model: function(params) {
    return posts.findBy('id', params.post_id);
  }
});

App.PostController = Ember.ObjectController.extend({
  isEditing: false,
  actions: {
    edit: function() {
      this.set('isEditing', true);
    },
    doneEditing: function() {
      this.set('isEditing', false);
    }
  }
});

var showdown = new Showdown.converter();

Ember.Handlebars.helper('format-markdown', function(input) {
  return new Handlebars.SafeString(showdown.makeHtml(input));
});

Ember.Handlebars.helper('format-date', function(date) {
  return moment(date).fromNow();
});
