"""
Views for the commitfollower app
"""

from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from .follower import get_repo_branches, unlink_user_branch, link_user_branch, get_recent_commits

@login_required
def feed(request):
	"""
	Return the news feed of commits for a user. To be consumed in an html template.
	"""
	context = RequestContext(request)
	commits = get_recent_commits(request.user, 10)

	return render_to_response('commitfollower/feed.html', {'commits': commits}, context_instance=context)

@login_required
def repo_list(request):
	"""
	Return a list of repositories for the logged in user. To be consumed in an html template.
	"""
	None


@login_required
def get_branches(request, repo_url):
	"""
	Get the branches for a repository. Returns a json payload.
	"""

	response_data = {}
	response_data['result'] = repo_url
	return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required
def follow_branches(request):
	"""
	Follow a list of branches.  Expects a json payload in post data.
	"""
	None

@login_required
def unfollow_branches(request):
	"""
	Unfollow a list of branches.  Expects a json payload in post data.
	"""
	None


@login_required
def remove_repo(request, repo_url):
	"""
	Remove the repo and all of it's branches from the followed list for the user.
	"""
	None

# class Repositories(View):
# 	@method_decorator(login_required)
# 	def dispatch(self, *args, **kwargs):
# 		""" Using dispatch allows the use of the login_required decorator """
# 		return super(Repositories, self).dispatch(*args, **kwargs)

# 	def get(self, request):
# 		""" Return a table of currently followed repositories """
# 		return render_to_response('', context_instance=RequestContext(request))

# 	def post(self, request):
# 		return render_to_response('', context_instance=RequestContext(request))
