//toggle for feed subscribe
var toggleFeed = function() {
	$(".toggleFeed").click(function() {
		if ($(this).hasClass('unsubscribed')) {
			var subscribe = '<button type="button" class="btn toggleFeed subscribed">Subscribed</button>';
			$(this).replaceWith(subscribe);
			$(this).css('color', '#FFF');
			sendOneWhisper();
			toggleFeed();
		} else {
			var unsubscribe = '<button type="button" class="btn toggleFeed unsubscribed">Subscribe</button>';
			$(this).replaceWith(unsubscribe);
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

$(document).ready(function() {
	//active navs
	var location = window.location.pathname.split('/').pop();
	$("#" + location + "nav").addClass("active");	
	toggleFeed();
});

