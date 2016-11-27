$(document).ready(function () {
    // This is for search on the index page
    $('#search-resources').submit(function(e) {
        e.preventDefault();
        console.log(document.querySelector('select').selectedOptions);
        var query = '?name=' + document.getElementById('search-resources-text').value;
        var options = document.querySelector('select').selectedOptions;
        for (var i = 0; i < options.length; i++) {
            query += '&' + 'option=' + options[i].label;
        }
        var endpoint = '/single-resource/search' + query;
        window.location.replace(endpoint);
    });
});
