$(function () {
  
    // menu tooltips
    (function () {
        'use strict'
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl)
        })
    })()

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
        $(anker).removeClass('hideContent').addClass('visibleContent');
        
        // set href for new-tab link
        current_location = $('.visibleContent').attr('src');
        $('#menu-newtab').attr('href', current_location)
    }

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