$(document).ready(function () {
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
        var options = document.querySelector('select').selectedOptions;
        if ($(this).val().length === 0 && options.length === 0) {
          window.location.replace('/single-resource/');
        }
    });
});

function searchQuery() {
  var query = '?name=' + $('#search-resources-text').val();
  var options = document.querySelector('select').selectedOptions;
  for (var i = 0; i < options.length; i++) {
    query += '&' + 'option=' + options[i].label;
  }
  var endpoint = '/single-resource/search' + query;
  window.location.replace(endpoint);
}
