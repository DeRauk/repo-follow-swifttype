"""
Views for the commitfollower app
"""

from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import json
from .follower import get_repo_branches, unlink_user_branch, link_user_branch, get_recent_commits
from .validators import valid_url, supported_vcs_provider, clean_url

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

	repo_url = clean_url(repo_url)

	# Errors: 400 - bad url, 501 not a supported vcs
	if not valid_url(repo_url):
		return HttpResponse(status=400)

	if not supported_vcs_provider(repo_url):
		return HttpResponse(status=501)

	try:
		branches = get_repo_branches(request.user, repo_url)
		response_data = {}
		response_data['success'] = True
		response_data['result'] = branches
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	except ObjectDoesNotExist:
		return HttpResponse(status=404)



@login_required
def updatebranches(request, repo_url):
	"""
	Updates followed branches for a repo.  Expects a json payload in post data.
	"""
	repo_url = clean_url(repo_url)

	None


@login_required
def remove_repo(request, repo_url):
	"""
	Remove the repo and all of it's branches from the followed list for the user.
	"""
	repo_url = clean_url(repo_url)

	# Some validation before we use repo_url in a db query
	if not valid_url(repo_url):
		return HttpResponse(status=400)

	if not supported_vcs_provider(repo_url):
		return HttpResponse(status=400)


	None
