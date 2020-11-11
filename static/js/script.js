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

    $(".addToReadBook").click(function() {
        $(".addReview").css("display", "none");
        $(".card").css("box-shadow", "none");
        $(this).next().show("slow");
        $(this).parent().css("box-shadow", "0px 0px 5px 2px rgba(0, 0, 0, 0.55)");
    });

    $(document).mouseup(function(e) {
        var reviewBox = $(".addReview");
        if (!reviewBox.is(e.target) && reviewBox.has(e.target).length === 0) {
            reviewBox.hide();
            reviewBox.parent().css("box-shadow", "none");
        }
    })

    $("#libraryPart").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(3)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(3)").show();
    });

    $("#readPart").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(4)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(4)").show();
    });

    $("#reviewPart").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(1)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(1)").show();
    });

    $("#quotePart").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(2)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(2)").show();
    });

    $(".searchButton").click(function() {
        let val = $(".searchInput").val();
    });


    $("#ratedBooks").click(function() {
        $(".statisticParts").children().not(":first-child").hide();
        $(".statisticParts").children(":first-child").show();
    });

    $("#mostAuthors").click(function() {
        $(".statisticParts").children().not(":nth-child(2)").hide();
        $(".statisticParts").children(":nth-child(2)").show();
    });

    $("#mostCategories").click(function() {
        $(".statisticParts").children().not(":nth-child(3)").hide();
        $(".statisticParts").children(":nth-child(3)").show();
    });



});