"""
Views for the commitfollower app
"""

from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.template import Context
from django.template.context import RequestContext
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .follower import RateLimitException
from . import follower
from .validators import valid_url, supported_vcs_provider, clean_url, repo_contains_branches

COMMIT_PAGE_SIZE = 25

@login_required
def feed(request):
	"""
	Return the news feed of commits for a user. Returns an html payload.
	"""
	return render_to_response('commitfollower/feed.html',
																	context_instance=RequestContext(request))

@login_required
def get_commits(request):
	"""
	Returns an html payload of commits, pass a page in as GET param. Defaults
		to page 1
	"""

	try:
		commits_list = follower.get_recent_commits(request.user)
	except RateLimitException:
		return HttpResponse(status=403)

	if len(commits_list) == 0:
		# User has no commits
		response = render_to_response('commitfollower/no_repos.html',
																			context_instance=RequestContext(request))
		response['more_pages'] = False
		return response
	else:
		paginator = Paginator(commits_list, COMMIT_PAGE_SIZE)
		page = request.GET.get('page')

		try:
			commits = paginator.page(page)
		except PageNotAnInteger:
			page = 1
			commits = paginator.page(page)
		except EmptyPage:
			commits = []

		response = render_to_response('commitfollower/commit_list.html',
																		{'commits': commits},
																			context_instance=RequestContext(request))
		response['more_pages'] = int(page) < paginator.num_pages

		return response

@login_required
def repo_list(request):
	"""
	Return a list of repositories for the logged in user. Returns an html payload.
	"""

	repos = follower.get_user_repos(request.user)

	return render_to_response('commitfollower/repository_list.html',
															{'repos': repos},
																context_instance=RequestContext(request))

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
		branches = follower.get_repo_branches(request.user, repo_url)
		repo = branches[0][0].repository

		parameters = {'branches': branches, 'repo':repo}
		html = get_template('commitfollower/branch_choice_modal.html')
		return HttpResponse(html.render(Context(parameters)))
	except ObjectDoesNotExist:
		return HttpResponse(status=404)
	except RateLimitException:
		return HttpResponse(status=403)

@login_required
def update_branches(request, repo_url):
	"""
	Updates followed branches for a repo.  Expects a json payload in post data.
	"""
	repo_url = clean_url(repo_url)

	# Some validation before we use repo_url in a db query
	if not valid_url(repo_url) or not supported_vcs_provider(repo_url):
		return HttpResponse(status=400)

	if request.method == 'POST':
		branch_names = request.POST.keys()
		if not repo_contains_branches(repo_url, branch_names):
			return HttpResponse(status=400)
		else:
			try:
				follower.add_remove_user_branches(request.user, repo_url, branch_names)
			except RateLimitException:
				return HttpResponse(status=403)
			return HttpResponse(status=200)
	else:
		return HttpResponse(status=501)


@login_required
def unfollow_repo(request, repo_url):
	"""
	Remove the repo's branches from the followed list for the user.
	"""
	repo_url = clean_url(repo_url)

	# Some validation before we use repo_url in a db query
	if not valid_url(repo_url):
		return HttpResponse(status=400)

	if not supported_vcs_provider(repo_url):
		return HttpResponse(status=400)

	try:
		user = request.user
		follower.unfollow_repo(user, repo_url)
		return HttpResponse(status=200)
	except ObjectDoesNotExist:
		return HttpResponse(status=404)
