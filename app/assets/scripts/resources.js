$(document).ready(function () {
    // This is for search on the index page
    $('#search-resources').submit(function(e) {
        e.preventDefault();
        console.log(document.getElementById('search-resources-options').value);
        var query = 'name=' + document.getElementById('search-resources-text').value + '&' + 'option=' + document.getElementById('search-resources-options').value;
        var endpoint = '/single-resource/' + query;
        //window.location.replace(endpoint);
    });
});
