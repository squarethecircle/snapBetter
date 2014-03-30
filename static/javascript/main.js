//function for snapta button
var toggleSnapta = function() {
	$(".toggleSnapta").click(function() {
		if ($(this).attr('id') == 'addsnapta') {
			var rmvSnapta = '<button type="button" class="btn toggleSnapta" id="rmvsnapta" val="rmv"><span class="glyphicon glyphicon-ok"></span> Secret Snapta</button>';
			$("#addsnapta").replaceWith(rmvSnapta);
			toggleSnapta();
		} else {
			var addSnapta = '<button type="button" class="btn toggleSnapta" id="addsnapta" val="add">Add Secret Snapta</button>';
			$("#rmvsnapta").replaceWith(addSnapta);
			toggleSnapta();
		}
	});

	$(function(){
		$("#rmvsnapta").hover(function(){
			$(this).html("Remove Secret Santa");

			$(this).css("background-color", "#D91E18");
		}, function(){
        // change to any color that was previously used.
        $(this).css("background-color", "#F25887");
        $(this).html('<span class="glyphicon glyphicon-ok"></span> Secret Snapta');
    });
	});
};

//toggle for feed subscribe
var toggleFeed = function() {
	$(".toggleFeed").click(function() {
		if ($(this).hasClass('unsubscribed')) {
			console.log('d');
			var subscribe = '<button type="button" class="btn toggleFeed subscribed">Subscribed</button>';
			$(this).replaceWith(subscribe);
			$(this).css('color', '#FFF');
			toggleFeed();
		} else {
			console.log('d');
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
	toggleSnapta();	
	toggleFeed();
});

