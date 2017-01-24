// Semantic UI breakpoints
var mobileBreakpoint = 768;
var tabletBreakpoint = 992;
var smallMonitorBreakpoint = 1200;

var singleColNoSpaceBreakpoint = 500;
var singleColBreakpoint = 800;
var twoColResizeBreakpoint = 1150;

$(document).ready(function () {

    // Enable dismissable flash messages
    $('.message .close').on('click', function () {
        $(this).parent().fadeOut();
    });

    // Enable mobile navigation
    $('#open-nav').on('click', function () {
        $('.mobile.only .vertical.menu').transition('slide down');
    });

    // Enable dropdowns
    $('.dropdown').dropdown();
    $('select').dropdown();
});


// Add a case-insensitive version of jQuery :contains pseduo
// Used in table filtering
(function ($) {
    function icontains(elem, text) {
        return (elem.textContent || elem.innerText || $(elem).text() || "")
                .toLowerCase().indexOf((text || "").toLowerCase()) > -1;
    }

    $.expr[':'].icontains = $.expr.createPseudo ?
        $.expr.createPseudo(function (text) {
            return function (elem) {
                return icontains(elem, text);
            };
        }) :
        function (elem, i, match) {
            return icontains(elem, match[3]);
        };
})(jQuery);

