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
        if ($(this).val().length === 0) {
          window.location.replace('/single-resource/');
        }
    });
});

function searchQuery() {
  var query = $('#search-resources-text').val();
  var endpoint = '/single-resource/' + query;
  window.location.replace(endpoint);
}