function ajaxCall(username, auth_token, request, params) {
	//determines friendship status with Snapta

	if (request == 'isSnaptaFriend') {

		$.ajax({

			url: $SCRIPT_ROOT+'requests',
			type: 'POST',
			
			data: { username: username, auth_token: auth_token, request: request },
			success: function(response) {

				if (response == 'friends') {
					if ($(".toggleSnapta").attr("id") == "addsnapta")
						alert(1);
						replaceToggle(changed);
				} else {
					if ($(".toggleSnapta").attr("id") == "rmvsnapta")
						alert("TEST");
						replaceToggle(changed);
				}
				$("#mainStyles").html($("#mainStyles").html());
				
			}
		});
	} else if (request == 'makeFriend') {
		$.ajax({
			url: $SCRIPT_ROOT+'requests',
			type: 'POST',
			data: { username: username, auth_token: auth_token, request: request, friend: params['friend'] },
			success: function(response) {
				if (response) {
					changed = true;
					ajaxCall(username, auth_token, 'isSnaptaFriend');
				}

			}
		});
	} else if (request == 'deleteFriend') {
		$.ajax({
			url: $SCRIPT_ROOT+'requests',
			type: 'POST',
			data: { username: username, auth_token: auth_token, request: request, friend: params['friend'] },
			success: function(response) {
				if (response) {
					changed = true;
					ajaxCall(username, auth_token, 'isSnaptaFriend');
				}
			}
		});
	}
};




