$(function () {

    var client_iframe_url;
  
    // menu tooltips
    (function () {
        'use strict'
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl)
        })
    })()

    function CheckOpenedVncTab(){
        try {
            // try opening a window
            var winref = window.open('', 'viewer-tab', '', true);
            // if it succeeded: No viewer-tab opened, close it
            if(winref.location.href === 'about:blank'){
                winref.close();
            }
            return false;
        } catch (error) {
            // if CORS-object error
            return true;
        }
    }

    if(CheckOpenedVncTab()) {
        client_iframe_url = $('#client').attr('src');
        $("#client").attr('src', '');
        $('.pager').addClass('hideContent').removeClass('visibleContent');
        $('#client-resume').removeClass('hideContent')
    }

    function toggleContent(href = null) {
        
        var default_anker = '#docs';
        var anker = null;

        if (!href) {
            anker = $(location).attr('hash');
        } else {
            anker = '#' + href.split('#')[1];
        }

        // define default anker
        if (!anker || anker == '#') {
            anker = default_anker;
        }

        var href = $(location).attr('pathname') + anker
        $('nav a').removeClass('active');
        $('nav a[href="' + href + '"]').addClass('active');
        
        // toggle content 
        $('.pager').addClass('hideContent').removeClass('visibleContent');

        if ((anker == '#client') && ($("#client").attr('src') == '')) {
            $('#client-resume').removeClass('hideContent')
        } else {
            $(anker).removeClass('hideContent').addClass('visibleContent');
        }   
        $(anker).addClass('visibleContent');     
        
        $('#menu-newtab').unbind().click(function() {newTab();})

    }
    
    function newTab() {
        current_location = $('.visibleContent').attr('src');

        if ($("#client").hasClass("visibleContent") &&
            $("#client").attr('src') != '') {
                // save location
                client_iframe_url = current_location
                // unload iframe
                $("#client").attr('src', '')
                // open noVNC in new tab
                let w = window.open(current_location, '_blank');
                w.name = "viewer-tab";

                $('.pager').addClass('hideContent').removeClass('visibleContent');
                $('#client-resume').removeClass('hideContent')
        } else {
            window.open(current_location, '_blank')
        }
    }

    $('#resume-btn').click(function() {
        // get control over tab
        let w = window.open("", "viewer-tab");
        // close tab
        w.close('viewer-tab')
        
        if(CheckOpenedVncTab()) {
            alert("Close tab manually")
        } else {   
            // return to iFrame viewer
            $("#client").attr('src', client_iframe_url)
            
            $('.pager').addClass('hideContent').removeClass('visibleContent');
            $('#client').removeClass('hideContent').addClass('visibleContent');
        }
    })

    // remove preloader
    $('#preloader').addClass('hideContent');

    // initial marking of menu
    toggleContent()

    // menu behaviour
    $('nav a').click(function() {
      toggleContent(href = $(this).attr("href"));
    })

    // chat toggle
    $('#menu-chat').click(function () {

        // mark menu item
        $(this).toggleClass('active');
        $('#chat-container').toggleClass('hideContent');

    })

});