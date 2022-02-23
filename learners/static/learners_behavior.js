var noVNC_clients = {};

$(function () {
    var resumeTemplate = $("#client-resume");

    $.each($(".novnc_client"), function () {
        key = $(this).attr("id");
        value = $(this).attr("src");
        noVNC_clients[key] = value;
    });

    // menu tooltips
    (function () {
        "use strict";
        var tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    })();

    // function CheckOpenedVncTab() {
    //     try {
    //         // try opening a window
    //         var winref = window.open("", "viewer-tab", "", true);
    //         // if it succeeded: No viewer-tab opened, close it
    //         if (winref.location.href === "about:blank") {
    //             winref.close();
    //         }
    //         return false;
    //     } catch (error) {
    //         // if CORS-object error
    //         return true;
    //     }
    // }

    // if (CheckOpenedVncTab()) {
    //     client_iframe_url = $("#client").attr("src");
    //     $("#client").attr("src", "");
    //     $(".pager").addClass("hideContent").removeClass("visibleContent");
    //     $("#client-resume").removeClass("hideContent");
    // }

    function toggleContent(href = null) {
        // anker is either given in 'href' parameter or in the url address,
        // if not the fallback '#docs' is used
        let anker = href
            ? "#" + href.split("#")[1]
            : $(location).attr("hash") || "#docs";
        console.log(anker);

        $("nav a").removeClass("active");
        $('nav a[href="' + ($(location).attr("pathname") + anker) + '"]').addClass(
            "active"
        );

        // toggle content
        $(".pager").addClass("hideContent").removeClass("visibleContent");
        $(anker).removeClass("hideContent").addClass("visibleContent");
    }

    $("#menu-newtab").click(function () {
        newTab();
    });

    function newTab() {
        let iframe = $(".visibleContent");

        if (iframe.hasClass("novnc_client")) {
            // Currently visible page is a noVNC instance

            // unload iframe
            let id = iframe.attr("id");
            let src = noVNC_clients[id];
            iframe.attr("src", "");
            iframe.addClass("opened hideContent").removeClass("visibleContent");

            // open new tab
            let newTab = window.open(src, "_blank");
            newTab.name = "noVNC_" + id;

            createResumePage(iframe, src);

            $(document).on("click", "#resume-btn", function () {
                let resumePage = $(this).closest(".resumePage");
                let id = resumePage.attr("id");
                closeTab("noVNC_" + id);
                reinitFrame(id, resumePage);
            });

            // FIX MENU TOGGLE WHEN OPENED IN TAB

            // $("#resume-btn").click(function () {

            //     // closeTab($(this).attr("value"));
            //     // initFrame($(this).attr("value"));

            //     // if (CheckOpenedVncTab()) {
            //     //     alert("Close tab manually");
            //     // } else {
            //     //     // return to iFrame viewer
            //     //     $("#client").attr("src", client_iframe_url);

            //     //     $(".pager").addClass("hideContent").removeClass("visibleContent");
            //     //     $("#client").removeClass("hideContent").addClass("visibleContent");
            //     // }
            // });
        } else {
            // Docs
            console.log("this is docs etc");
        }

        // if (
        //     $("#client").hasClass("visibleContent") &&
        //     $("#client").attr("src") != ""
        // ) {
        //     // save location
        //     client_iframe_url = current_location;
        //     // unload iframe
        //     $("#client").attr("src", "");
        //     // open noVNC in new tab
        //     let w = window.open(current_location, "_blank");
        //     w.name = "viewer-tab";

        //     $(".pager").addClass("hideContent").removeClass("visibleContent");
        //     $("#client-resume").removeClass("hideContent");
        // } else {
        //     window.open(current_location, "_blank");
        // }
    }

    // function newTab() {
    //     var current_location = $('.visibleContent').attr('src');
    //     var current_client = $(".novnc_client.visibleContent")

    //     console.log(current_client)

    //     if (current_client &&
    //         current_client.attr('src') != '') {
    //         console.log("opened")
    //         // save location
    //         client_iframe_url = current_location
    //         // unload iframe
    //         current_client.attr('src', '')
    //         // open noVNC in new tab
    //         let w = window.open(current_location, '_blank');
    //         w.name = "viewer-tab";

    //         // ###########################################################################################
    //         // ###########################################################################################
    //         // ########################### ADD SUPPORT FOR MULTIPLE CLIENTS ##############################
    //         // Generate Resume view in js (per client)
    //         // new window with unique name
    //         // resume correct client
    //         //
    //         // ###########################################################################################
    //         // ###########################################################################################
    //         $('.pager').addClass('hideContent').removeClass('visibleContent');
    //         $('#client-resume').removeClass('hideContent')
    //     } else {
    //         window.open(current_location, '_blank')
    //     }
    // }

    function createResumePage(iframe, src) {
        let resumePage = resumeTemplate.clone();
        resumePage
            .attr("id", iframe.attr("id"))
            .addClass("resumePage visibleContent")
            .removeClass("hideContent");

        // Add src to the resume-button
        resumePage.find("#resume-btn").attr("value", src);
        // Append resume page to main
        iframe.parent().append(resumePage);
    }

    function closeTab(tabID) {
        let tab = window.open("", tabID);
        tab.close(tabID);
    }

    function reinitFrame(id, resumePage) {
        let iframe = $("#" + id + ".opened");
        iframe.attr("src", noVNC_clients[id]);
        iframe.addClass("visibleContent").removeClass("hideContent");
        resumePage.remove();
    }

    // remove preloader
    $("#preloader").addClass("hideContent");

    // initial marking of menu
    toggleContent();

    // menu behaviour
    $("nav a").click(function () {
        toggleContent($(this).attr("href"));
    });

    // chat toggle
    $("#menu-chat").click(function () {
        // mark menu item
        $(this).toggleClass("active");
        $("#chat-container").toggleClass("hideContent");
    });
});
