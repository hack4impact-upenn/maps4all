$(document).ready(function () {
    // This is for search on the index page
    $('#search-resources').submit(function(e) {
        e.preventDefault();
        var query = document.getElementById('search-resources-text').value;
        console.log(query);
        var endpoint = '/single-resource/' + query;
        if (query.length == 0) {
            endpoint = '/single-resource/';
        }
        window.location.replace(endpoint);
    });
});
