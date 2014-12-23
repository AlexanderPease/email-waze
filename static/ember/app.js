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
  location: 'hash'
});

/*******************************************************************************
Search
*******************************************************************************/
App.SearchRoute = Ember.Route.extend({
  model: function() {
    return $.getJSON('/search?domain=usv.com&name=').then(function(resp){
      console.log(resp);
      return resp.data;
    });
  }
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

App.AdminRoute = Ember.Route.extend({
  model: function() {
    return $.getJSON('/admin').then(function(resp){
      console.log(resp);
      return resp.data;
    });
  }
});


App.PostsRoute = Ember.Route.extend({
  model: function() {
    return $.getJSON('http://tomdale.net/api/get_recent_posts/?callback=?').then(function(data){
      console.log(data);
      return data.posts.map(function(post){
        post.body = post.content;
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
