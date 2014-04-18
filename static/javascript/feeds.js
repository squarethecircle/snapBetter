$(document).ready(function() {
	toggleFeed();

});


var whisperSubscribed = function(username, auth_token) {
	$.ajax({

		url: $SCRIPT_ROOT+'requests',
		type: 'POST',
		data: { username: username, auth_token: auth_token, request: 'isWhisperSubscribed' },
		success: function(response) {
			if (response == 'yes') {
				var subscribe = '<button type="button" id="whisperButton" class="btn toggleFeed subscribed">Subscribed</button>';
				$("#whisperButton").replaceWith(subscribe);
				$("#whisperButton").css('color', '#FFF');
				toggleFeed();
			} else {
				var unsubscribe = '<button id="whisperButton" type="button" class="btn toggleFeed unsubscribed">Subscribe</button>';
				$("#whisperButton").replaceWith(unsubscribe);
				toggleFeed();

			}
			$("#mainStyles").html($("#mainStyles").html());

		}

	});
};

//toggle for feed subscribe
var toggleFeed = function() {
	$(".toggleFeed").click(function() {
		if ($(this).hasClass('unsubscribed')) {
			var subscribe = '<button type="button" id="whisperButton" class="btn toggleFeed subscribed">Subscribed</button>';
			$(this).replaceWith(subscribe);
			$(this).css('color', '#FFF');
			subscribeWhisper();
			toggleFeed();
		} else {
			var unsubscribe = '<button id="whisperButton" type="button" class="btn toggleFeed unsubscribed">Subscribe</button>';
			$(this).replaceWith(unsubscribe);
			$(this).css('color', '#FFF');
			$.ajax({
				url: '/requests',
				type: 'POST',
				data: { 'username': "{{session['username']}}", 'auth_token':"{{session['auth_token']}}", 'request': 'makeFriend', 'friend': 'whisper_feed'},
				success: function (response) {
					if (response == 'success')
						console.log('whisper unsubscribed');
				}
			});
			toggleFeed();
		}
	});

	$(function(){
		$(".subscribed").hover(function(){
			$(this).html("Unsubscribe");
			$(this).css("background-color", "#D91E18");
			$(this).css("color", "#FFF");
		}, function(){
			$(this).css("background-color", "#F25887");
			$(this).html('Subscribed');
		});
	});
};

function subscribeWhisper() {
	$.ajax({
		url: '/subscribewhisper',
		type: 'POST',
		data: { 'username': "{{session['username']}}", 'auth_token':"{{session['auth_token']}}"},
		success: function (response) {
			if (response == 'success')
				console.log('whisper sent');
		}
	});
}

