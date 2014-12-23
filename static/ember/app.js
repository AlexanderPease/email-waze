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
