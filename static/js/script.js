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

    $(window).scroll(function() {

        if ($(window).scrollTop() > 100) {
            $(".backtotop").fadeIn();
        } else {
            $(".backtotop").fadeOut();
        }

    });

    $(".backtotop").click(function() {
        $("html,body").animate({
            scrollTop: 0
        }, 700);
        return false;
    });

    $(".addBookForm").click(function() {
        $("#addBookFormId").show("fast");
    });
});