 

$(document).ready(function() {
	//active navs
	var location = window.location.pathname.split('/').pop();
	$("#" + location + "nav").addClass("active");	
 });

