let nIntervId;
let currentNotificationID = null;

async function getNotification(endpoint) {
	if (!endpoint) endpoint = `/notification/last`;

	let response = await fetch(endpoint);

	if (response.status != 200) {
		console.log(response.statusText);
	} else {
		let message = await response.json();

		if (message.notifications.length) {
			$('#notification-container ul li').fadeOut(300, function () {
				$(this).remove();
			});
		}

		message.notifications.forEach(function (notification) {
			currentNotificationID = notification.id;

			const htmlNotification = `
            <li id="${notification.id}" visibility_control="${notification.position}">
                ${notification.msg}
                <div class="prev" onclick="getNotification('/notification/prev/${currentNotificationID}')"><svg class="bi" width="22" height="22" role="img"><use xlink:href="#icon_prev"></use></svg></div>
                <div class="next" onclick="getNotification('/notification/next/${currentNotificationID}')"><svg class="bi" width="22" height="22" role="img"><use xlink:href="#icon_next"></use></svg></div>
                <div class="closer" onclick="hideNotification(${currentNotificationID})"><svg class="bi" width="22" height="22" role="img"><use xlink:href="#icon_close"></use></svg></div>
            </li>`;

			if (checkNotificationVisibility(htmlNotification)) {
				$(htmlNotification)
					.hide()
					.appendTo('#notification-container ul')
					.slideDown(400);
			} else {
				$(htmlNotification)
					.hide()
					.appendTo('#notification-container ul');
			}
		});
		updateCounter(message.totalNotifications);
	}
}

function hideNotification(currentNotificationID) {
	$(`#notification-container ul #${currentNotificationID}`).fadeOut(300);
}

function setNotificationPolling(poll) {
	if (poll == 'active' && !nIntervId) {
		getNotification(`/notification/force_last`);
		nIntervId = setInterval(getNotification, 10000);
	} else {
		clearInterval(nIntervId);
		nIntervId = null;
		$('#notification-container ul li').fadeOut(300);
	}
}

function toggleNotification(btn) {
	// Toggle state
	const newState = $(btn).attr('state') == 'active' ? 'inactive' : 'active';
	$(btn).attr('state', newState);

	setNotificationPolling(newState);

	if (newState == 'inactive') {
		// add strike trough
		$(btn)
			.find('svg use')
			.first()
			.attr('xlink:href', '#icon_notification_inactive');
		$(btn).find('.tab_index').fadeOut(200);
		updateCounter(0);
	} else {
		// remove strike through
		$(btn)
			.find('svg use')
			.first()
			.attr('xlink:href', '#icon_notification_active');
		$(btn).find('.tab_index').fadeIn(200);
	}
}

function updateCounter(count) {
	if (count > 0) {
		$('#menu-notification').find('.tab_index').fadeIn(200);
		$('#menu-notification .tab_index span').html(count);
	} else {
		$('#menu-notification').find('.tab_index').fadeOut(200);
	}
}

function initNotificationBtn() {
	updateCounter(0);
	$('#menu-notification').click(function () {
		toggleNotification(this);
	});
}

function updateNotificationVisibility() {
	$('#notification-container ul li').each(function (index, notification) {
		if (checkNotificationVisibility($(notification))) {
			$(this).fadeIn(300);
		} else {
			$(this).fadeOut(150);
		}
	});
}

function checkNotificationVisibility(notification) {
	const visibility_control = $(notification).attr('visibility_control');
	if (
		($(`.${visibility_control}`).hasClass('visibleContent') ||
			visibility_control == 'all') &&
		$('#menu-notification').attr('state') == 'active'
	) {
		return true;
	} else {
		return false;
	}
}

$(function () {
	setNotificationPolling('active');
	initNotificationBtn();
	$('#navigation a')
		.not('#menu-notification')
		.click(function () {
			updateNotificationVisibility();
		});
});
