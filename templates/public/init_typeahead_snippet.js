// Init typeahead.js for #form-q input
// Put "include" statement in $(document).ready
var companies = new Bloodhound({
  datumTokenizer: function (datum) {
    console.log(datum);
    return Bloodhound.tokenizers.whitespace(datum.name);
  },
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  prefetch: {
    url: '/json/company_list.json',
    filter: function (companies_list) {
      // Map the remote source JSON array to a JavaScript object array
      return $.map(companies_list, function (company) {
        return {
          name: company.name,
          logo: company.logo,
          id: company.id
        };
      });
    }
  }
});

// Initialize the Bloodhound suggestion engine
//companies.clearPrefetchCache(); // Force reload from server
var promise = companies.initialize();
promise.done(function() {console.log('Bloodhound initialized!')});
 
// passing in `null` for the `options` arguments will result in the default
// options being used
$('#form-q').typeahead(null, {
  name: 'company',
  displayKey: 'name',
  source: companies.ttAdapter(),
  templates: {
    header: '<div class="tt-suggestion-heading"><strong>Companies</strong></div>',
    suggestion: Handlebars.compile('<img src="{{!logo}}" width="25px" height="25px"/>{{!name}}')
  }
});

