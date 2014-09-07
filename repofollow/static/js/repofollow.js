follower = {
	page: 0,
	more_commits: true,

	get_branches: function (repo_url){
		this.show_modal_spinner();
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
		}).done(function(data){
			follower.hide_modal_spinner();
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
		this.show_modal_spinner();
		$.ajax({
			type:"POST",
			url: $("#branch_update").attr("action"),
			data: $("#branch_update").serialize(),
		   statusCode: {
		      200: function (response) {
		      	 // loading gif off
		         location.reload();
		      },
		      400: function (response) {
		         follower.client_error("Invalid url entered for a repository");
		         $("#branch_modal").modal('hide');
		      },
		      404: function(response) {
		      	follower.client_error("We could not find a repository at that url");
		      	$("#branch_modal").modal('hide');
		      },
		      501: function (response) {
		         follower.client_error("Sorry, we currently only support repositories on github.com");
		         $("#branch_modal").modal('hide');
		      }
		   }
		}).done(function(data){
			follower.hide_modal_spinner();
		});
	},

	unfollow_repo: function(rest_url){
		$.ajax(rest_url, {
		   type: "GET",
		   statusCode: {
		      200: function (response) {
		         location.reload();
		      },
		      400: function (response) {
		         follower.client_error("Invalid repository url or branch");
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

	load_more_commits: function(rest_url){
		$(".loadmore a").hide();
		$(".loadmore i").show();
		this.page += 1;

		$.ajax(rest_url + "?page=" + this.page, {
		   type: "GET",
		   statusCode: {
		      200: function (response) {
		         $("#commits").append(response);
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
		}).success(function(data, textStatus, request){
			if(request.getResponseHeader('more_pages') == 'True'){
				follower.more_commits = false;
			}
			console.log(request.getResponseHeader('more_pages'));
		}).done(function(data) {
			$(".loadmore i").hide();
			if(follower.more_commits){
				$(".loadmore a").show();
			}
		});
	},

	show_modal_spinner: function(){
		$("#overlayspinner").show();
	},

	hide_modal_spinner: function(){
		$("#overlayspinner").hide();
	}
};
