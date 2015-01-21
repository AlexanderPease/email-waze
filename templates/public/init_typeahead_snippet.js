// Init typeahead.js for #form-q input
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

/* Trigger search when a suggestion is selected 
  Sends a request using <field>_id to specify exact document to look up */
$('#form-q').bind('typeahead:selected', function(obj, datum, name){
  // obj is event, datum is what I've given typeahead, name is "company"
  var field = name; 
  // Reload datatable
  var new_url = 'api/searchbaseprofileconnection?' + field + '_id=' + datum['id'];
  console.log(new_url)
  $("#search_table").DataTable().ajax.url(new_url).load();
  displayLoading();
  showCompanyPanel(datum);
  //window.location.href.replace("name="+name, "domain="+domain); // not working
});