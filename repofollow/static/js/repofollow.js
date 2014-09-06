follower = {
	get_branches: function (){
		var repo_url = $("input#repo_url").val();

		$.ajax("/follower/branches/" + repo_url, {
		   type: "GET",
		   statusCode: {
		      200: function (response) {
		         follower.show_add_branches(response);
		      },
		      400: function (response) {
		         follower.client_error("Invalid url entered for a repository");
		      },
		      404: function(response) {
		      	follower.client_error("We could not find a repository at that url");
		      },
		      501: function (response) {
		         follower.client_error("Sorry, we currently only support repositories on github.com");
		      }
		   }
		});
	},

	client_error: function(msg){
		$("#error_message").html(msg);
		$(".alert#client_error").show();
	},

	show_add_branches: function(response){
		$("#modal_placeholder").html(response);
		$("#modal_placeholder .modal").modal();
	},

	branch_update: function(){
		$.ajax({
			type:"POST",
			url: $("#branch_update").attr("action"),
			data: $("#branch_update").serialize(),
			beforeSend: function(){
				// loading gif;
			},
			success: function(data){
				location.reload();
			}
		});
	}
};
