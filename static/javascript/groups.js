
var addFriend = function(element) {
	var friend = element.clone();
	element.remove();
	$(".group > ul").append(friend);
	$(".group > ul > li:last").click(function(){
		rmFriend($(this));
	});

}

var rmFriend = function(element) {
	var friend = element.clone();
	element.remove();
	$(".friends > ul").append(friend);
	$(".friends > ul > li:last").click(function(){
		addFriend($(this));
	});
}



$(document).ready(function() {
	
	$(".arrow").css("top", "-" + (parseInt($(".friends > ul").css("height")) / 2) + "px");

	getFriends();

});
