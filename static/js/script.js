$(document).ready(function() {

    $("#navbarCollapse").click(function() {
        $(".profileExtension").toggle("fast");
        $(this).toggleClass("rotate180deg");
    })

    $("#reviewButton").click(function() {
        $("#reviews").css("display", "inline");
        $("#quotes").css("display", "none");
    })

    $("#quoteButton").click(function() {
        $("#reviews").css("display", "none");
        $("#quotes").css("display", "inline");
    })

});