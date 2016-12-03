$(document).ready(function () {

    // This is for search on the index page
    // Currently searches by descriptor name only
    $('#search-descriptors').keyup(function () {
        var searchText = $(this).val();
        if (searchText.length > 0) {
            $('tbody td.descriptor-name:icontains(' + searchText + ')').addClass('positive');
            $('td.descriptor-name.positive').not(':icontains(' + searchText + ')').removeClass('positive');
            $('tbody td.descriptor-name').not(':icontains(' + searchText + ')').closest('tr').addClass('hidden').hide();
            $('tr.hidden:icontains(' + searchText + ')').has('td.descriptor-name:icontains(' + searchText + ')').removeClass('hidden').show();
        } else {
            $('td.descriptor-name.positive').removeClass('positive');
            $('tr.hidden').removeClass('hidden').show();
        }
    });

    // This is for the deletion checkbox on the manage descriptors page
    $('.deletion.checkbox').checkbox({
        onChecked: function() {
            $('.deletion.button').removeClass('disabled');
        },
        onUnchecked: function() {
            $('.deletion.button').addClass('disabled');
        }
    });

    // This is for the new descriptor page
    $("#desc_type").change(function() {
        if ($(this).val() === "Option") {
            $("#values-div").show();
        } else {
            $("#values-div").hide();
        }
    });
});
