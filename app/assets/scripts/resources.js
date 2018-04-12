$(document).ready(function () {
    // Import jquery-tablesort.js method to make resource table sortable
    $('#resources-table').tablesort()

    // This is for search on the index page
    // Search resources by name
    $('#search-resources').click(searchQuery); // click submit button
    $('#search-resources-text').keypress(function(e) { // press enter key
      if (e.which == 13) {
         e.preventDefault();
         searchQuery();
      }
    });
    // Show all resources when deleted the search query
    $('#search-resources-text').keyup(function () {
        var requiredOptions = [];
        $("#search-resources-req-options :selected").each(function() {
          requiredOptions.push($(this).val());
        });
        if ($(this).val().length === 0 && requiredOptions.length === 0) {
          window.location.replace('/single-resource/');
        }
    });
});

function searchQuery() {
  var query = '?name=' + $('#search-resources-text').val();
  // var required_options = document.querySelector('select').selectedOptions;
  var requiredOptions = [];
  $("#search-resources-req-options :selected").each(function() {
    requiredOptions.push($(this).val());
  });
  for (var i = 0; i < requiredOptions.length; i++) {
    query += '&reqoption=' + requiredOptions[i];
  }
  var endpoint = '/single-resource/search' + query;
  window.location.replace(endpoint);
}
