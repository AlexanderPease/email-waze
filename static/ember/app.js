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

App.SearchRoute = Ember.Route.extend({
  model: function() {
    return 'foo';
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
