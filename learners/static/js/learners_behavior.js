var noVNC_clients = {};

$(function () {
  $.each($(".graphs"), function () {
    let g = $(this)[0];
    let labels = $(g).attr("labels").split("; ");
    let counts = $(g).attr("counts").split("; ");
    let backgroundColors = $(g).attr("backgroundColors").split("; ");
    buildChart(g.getContext("2d"), labels, counts, backgroundColors);
  });

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

  $("#menu-newtab").click(function () {
    newTab();
  });

  // remove preloader
  $("#preloader").addClass("hideContent");

  // initial marking of menu
  toggleContent();

  // menu behaviour
  $("nav a")
    .not(".external-link")
    .click(function () {
      toggleContent($(this).attr("href"));
    });

  // chat toggle
  $("#menu-chat").click(function () {
    // mark menu item
    $(this).toggleClass("active");
    $("#chat-container").toggleClass("hideContent");
  });

  $("table td").hover(
    function () {
      var row = $(this).parent();
      var col = $(this)
        .parent()
        .parent()
        .find("th, td")
        .filter(`:nth-child(${$(this).index() + 1})`);
      row.addClass("marked");
      col.addClass("marked");
    },
    function () {
      var row = $(this).parent();
      var col = $(this)
        .parent()
        .parent()
        .find("th, td")
        .filter(`:nth-child(${$(this).index() + 1})`);
      row.removeClass("marked");
      col.removeClass("marked");
    }
  );

  $("table td").click(function () {
    var link = $(this).find("input").val();
    if (link) {
      location.href = link;
    }
  });

  $("#exercises-select").change(function () {
    let index = $(`table th:has(input[value='${$(this).val()}'])`).index() + 1;
    let cells = $(`table th, table td`);

    if (index == 0) {
      cells.fadeIn("slow");
    } else {
      cells.not(`:nth-child(-n +2)`).hide();
      cells.filter(`:nth-child(-n +2)`).show();
      cells.filter(`:nth-child(${index})`).fadeIn("slow");
    }
  });

  $("#users-select").change(function () {
    var index =
      $(`table tr td:contains('${$(this).val()}')`)
        .parent()
        .index() + 1;

    if (index == 0) {
      $(`table tr`).fadeIn("slow");
    } else {
      $(`table tr`).not(`:nth-child(1)`).hide();
      $(`table tr`).filter(`:nth-child(${index})`).fadeIn("slow");
    }
  });

  disableBackButton();
});

/**
 * This function is used to open the currently active/visible content in a new tab.
 * Depending on whether a noVNC client or a normal page is currently active, the
 * local content is duplicated or replaced by a temporary resume page that can also
 * close the open tab again.
 */

function newTab() {
  let iframe = $(".visibleContent");
  let id = iframe.attr("id");

  if (iframe.hasClass("novnc_client")) {
    // Currently visible page is a noVNC instance

    // unload iframe
    let original_url = noVNC_clients[id];
    iframe.attr("src", "");
    iframe.addClass("opened hideContent").removeClass("visibleContent");

    // open new tab
    let newTab = window.open(original_url, "_blank");
    newTab.name = `noVNC_${id}`;

    // Create DOM object from the resume-Page template
    createResumePage(iframe, original_url);

    // init button functionality of created DOM object
    $(document).on("click", "#resume-btn", function () {
      let resumePage = $(this).closest(".resumePage");
      let id = resumePage.attr("id");
      closeTab(`noVNC_${id}`);
      reinitFrame(id, resumePage);
    });
  } else {
    // Currently visible page is NOT a noVNC instance

    let src = iframe.attr("src");
    if (src) {
      // open new tab
      let newTab = window.open(src, "_blank");
      newTab.name = `${id}_tab`;
    }
  }
}

/**
 * This function is responsible for switching the visible content. It does
 * this depending on the hash of the url or on the clicked icon in the nav bar.
 * Furthermore it distinguishes if a VNC client is opened in a new tab and
 * therefore the resume page is displayed.
 *
 * @param {*} href      url with target hash (default = null)
 */

function toggleContent(href = null) {
  // anker is either given in 'href' parameter or in the url address,
  // if not the fallback '#documentation' is used
  let baseurl = $(location).attr("pathname");
  let anker = "";

  let landingpage = window.landingpage
  if (!window.landingpage) landingpage = "#documentation"
  if (window.landingpage == "novnc") {
    // get first novnc container
    landingpage = $(".novnc_client").first().attr("id")
  }

  if (baseurl == "/access") {
    anker = href
      ? `#${href.split("#")[1]}`
      : $(location).attr("hash") || `#${landingpage}`;
  }

  // toggle menu active
  $("nav a").removeClass("active");
  if (anker) {
    $(`nav a[href="${baseurl}${anker}"]`).addClass("active");
  } else {
    $(`nav a[href^="/${baseurl.split("/")[1]}"]`).addClass("active");
  }

  // toggle content
  $(".pager").addClass("hideContent").removeClass("visibleContent");

  let resumePage = $(`${anker}.resumePage`);
  if (resumePage.length) {
    resumePage.removeClass("hideContent").addClass("visibleContent");
  } else {
    $(anker).removeClass("hideContent").addClass("visibleContent");
  }
}

/**
 * This function creates the resume page which allows the participant
 * to continue the noVNC session after opening the tab here.
 * For this purpose, the existing template in the DOM is cloned,
 * adapted and inserted into the DOM.
 *
 * @param {*} iframe        associated iFrame
 * @param {*} original_url  src of the original iFrame
 */

function createResumePage(iframe, original_url) {
  let resumeTemplate = $("#client-resume");
  let resumePage = resumeTemplate.clone();
  resumePage
    .attr("id", iframe.attr("id"))
    .addClass("resumePage visibleContent")
    .removeClass("hideContent");
  resumePage.find("h2").html(`Resume ${iframe.attr("name")} here`);

  // Add original_url to the resume-button
  resumePage.find("#resume-btn").attr("value", original_url);
  // Append resume page to main
  iframe.parent().append(resumePage);
}

/**
 * Function used to close an opened tab
 *
 * @param {*} tabID     window name of opened tab
 */

function closeTab(tabID) {
  let tab = window.open("", tabID);
  tab.close(tabID);
}

/**
 * Function to reinitialize a iFrame after the opened Tab has been closed.
 *
 * @param {*} id            target iFrame ID
 * @param {*} resumePage    resume-Page to be removed
 */

function reinitFrame(id, resumePage) {
  let iframe = $(`#${id}.opened`);
  iframe.attr("src", noVNC_clients[id]);
  iframe.addClass("visibleContent").removeClass("hideContent");
  resumePage.remove();
}

function buildChart(ctx, labels, counts, backgroundColors) {
  const data = {
    labels: labels,
    datasets: [
      {
        data: counts,
        backgroundColor: backgroundColors,
        borderWidth: 0,
      },
    ],
  };

  const chart = new Chart(ctx, {
    type: "doughnut",
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: 30,
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
}

function execSetDrawIO(url_encoded_data) {
  let iframe = $("#drawio");
  if (iframe) {
    let original_src = iframe.attr("src");
    let host = original_src.split("?title=")[0];
    iframe.attr("src", `${host}/${url_encoded_data}`);
    toggleContent("/access#drawio");
  } else {
    let newTab = window.open(
      `https://app.diagrams.net/${url_encoded_data}`,
      "_blank"
    );
    newTab.name = `drawio_tab`;
  }
}

function disableBackButton() {
  window.history.pushState(null, null, window.location.href);
  window.onpopstate = function () {
    window.history.go(1);
  };
}
