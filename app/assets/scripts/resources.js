$(document).ready(function () {
    // This is for search on the index page
    $('#search-resources').submit(function(e) {
        e.preventDefault();
        var query = document.getElementById('search-resources-text').value;
        var endpoint = '/single-resource/' + query;
        window.location.replace(endpoint);
    });
});
