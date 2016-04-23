$(document).ready(function () {

    // This is for search on the index page
    $('#search-descriptors').keyup(function () {
        var searchText = $(this).val();
        if (searchText.length > 0) {
            $('tbody td:icontains(' + searchText + ')').addClass('positive');
            $('td.positive').not(':icontains(' + searchText + ')').removeClass('positive');
            $('tbody td').not(':icontains(' + searchText + ')').closest('tr').addClass('hidden').hide();
            $('tr.hidden:icontains(' + searchText + ')').removeClass('hidden').show();
        } else {
            $('td.positive').removeClass('positive');
            $('tr.hidden').removeClass('hidden').show();
        }
    });

    $('#select-type').dropdown({
        onChange: function (value, text, $selectedItem) {
            $('td.descriptor.type:contains(' + value + ')').closest('tr').removeClass('hidden').show();
            $('td.descriptor.type').not(':contains(' + value + ')').closest('tr').addClass('hidden').hide();
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
