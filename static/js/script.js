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

    $("#follows").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(5)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(5)").show();
    });

    $("#followNum").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(5)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(5)").show();
    });

    $("#followers").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(6)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(6)").show();
    });

    $("#followerNum").click(function() {
        $(".col-7 .cardGroup12").children().not(":nth-child(6)").hide();
        $(".col-7 .cardGroup12").children(":nth-child(6)").show();
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

    $(".psIcon").click(function() {
        $(this).toggleClass('fa-eye');
        $(this).toggleClass('fa-eye-slash');
        if ($(this).hasClass('fa-eye-slash')) {
            $("#passwordInput").attr("type", "password");
        } else {
            console.log("text olması lazım");
            $("#passwordInput").attr("type", "text");
        }
    });

    $(document).mouseup(function(e) {
        var reviewBox = $("#addBookFormId");
        var readlistList = $(".readlistList");
        var searchresults = $(".searchresults");
        var notif = $(".notificationdiv");
        var notif2 = $(".notification");

        if (!reviewBox.is(e.target) && reviewBox.has(e.target).length === 0) {
            reviewBox.hide();
            reviewBox.parent().css("box-shadow", "none");
        }
        if (!readlistList.is(e.target) && readlistList.has(e.target).length === 0) {
            readlistList.hide();
        }
        if (!searchresults.is(e.target) && searchresults.has(e.target).length === 0) {
            searchresults.hide();
        }
        if (!notif.is(e.target) && notif.has(e.target).length === 0) {
            if (!notif2.is(e.target) && notif2.has(e.target).length === 0)
            {
                notif.hide();
            }
        }
    });

    $(".addtoreadlist").click(function() {
        $(this).next().children(":first-child").show();
    })
    $(".addQuoteButton").click(function() {
        $(this).next().show();
    })

    $(".dotdiv").click(function(){
        console.log("deneme");
        let x = 90
        $(this).toggleClass("turn90");
        $(this).next().children().toggle(500);
        $(this).next().next().toggle(500);
    })

    $(".trendchoice:first-child").click(function(){
        $(".trendbooks").show();
        $(".trendauthors").hide();
    })

    $(".trendchoice:nth-child(2)").click(function(){
        $(".trendbooks").hide();
        $(".trendauthors").show();
    })


    $("#searchId").on("input", function(e){
        textInput = $("#searchId").val();
        $.ajax({
            method: "post",
            url: "/livesearch",
            data: {text: textInput},
            success: function(res){
                    var data = "";
                    $.each(res,function(index,value){
                        if(value[3] == 0){
                            data += "<li><a href='/books/"+value[0]+"'>"+value[1]+"</a></li>";  
                        } else {
                            data += "<li><a href='/authors/"+value[0]+"'>"+value[1]+"</a></li>";  
                        }
                    });
                    $(".searchresults").css("display","inherit");
                    $(".searchresults").html(data);
            }
        })
    })

    $(".fa-chevron-circle-up").click(function(){

        $(".notificationdiv").hide("fast");
        $(this).parent().parent().toggleClass("bottom380");
        $(this).toggleClass("rotate180deg");
        setTimeout(() => {  $(".profCard").toggle(300); }, 300);
        
    })

    $(".notification").click(function(){
        $(".profCard").hide(300)
        $(".fa-chevron-circle-up").parent().parent().removeClass("bottom380");
        $(".fa-chevron-circle-up").removeClass("rotate180deg");
        $(".notification2 .fa-circle").remove();
        $.ajax({
            method: "post",
            url: "/getnotification",
            success: function(res){
                var data = "";
                var ids = [];
                $.each(res, function(index, value){
                    if(value[0] == 0){
                        data += "<li class='active'><a class='active' href='users/"+value[2]+"'>"+value[1]+"&nbsp;</a> follows you <i class='fas fa-circle'></i></li>";
                        ids.push(value[2]);
                    } else {
                        data += "<li class='text-pas'><a class='text-pas' href='users/"+value[2]+"'>"+value[1]+"&nbsp;</a> follows you </li>";
                    }
                })
                $(".notificationInDiv").html(data);
                $(".notificationdiv").toggle("fast");
                
                $.ajax({
                    method: "post",
                    url: "/readnotification",
                    data: {text: ids}
                })
            }
        })
    })

    function yourFunction(){
        
        $.ajax({
            method: "post",
            url: "/getnotification",
            success: function(res){
                var check = 0;
                $.each(res, function(index, value){
                    if(value[0] == 0){
                        check = 1;
                    }
                })
                if(check == 1){
                    $(".notification2").append("<i class='fas fa-circle'></i>")
                }
            }
        })
        setTimeout(yourFunction, 1000);
    }
    
    yourFunction();



});
