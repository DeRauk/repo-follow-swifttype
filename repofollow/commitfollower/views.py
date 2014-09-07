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
from . import follower
from .validators import valid_url, supported_vcs_provider, clean_url, repo_contains_branches
import logging, pdb

logger = logging.getLogger(__name__)

@login_required
def feed(request):
	"""
	Return the news feed of commits for a user. Returns an html payload.
	"""
	context = RequestContext(request)
	return render_to_response('commitfollower/feed.html', context_instance=context)

@login_required
def get_commits(request):
	"""
	Returns an html payload of commits.
	"""
	context = RequestContext(request)

	commits_list = follower.get_recent_commits(request.user)

	if len(commits_list) == 0:
		response = render_to_response('commitfollower/no_repos.html',
																			context_instance=context)
		response['more_pages'] = False
		return response
	else:
		paginator = Paginator(commits_list, 3)
		page = request.GET.get('page')

		try:
			commits = paginator.page(page)
		except PageNotAnInteger:
			page = 1
			commits = paginator.page(page)
		except EmptyPage:
			page = paginator.num_pages
			commits = paginator.page(page)

		response = render_to_response('commitfollower/commit_list.html', {'commits': commits},
																	context_instance=context)
		response['more_pages'] = int(page) < paginator.num_pages

		return response

@login_required
def repo_list(request):
	"""
	Return a list of repositories for the logged in user. Returns an html payload.
	"""

	context = RequestContext(request)
	repos = follower.get_user_repos(request.user)

	return render_to_response('commitfollower/repository_list.html',
															{'repos': repos}, context_instance=context)


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
		branch_models = follower.get_repo_branches(request.user, repo_url)
		display_data = [(b.name, followed) for b, followed in branch_models]
		parameters = {'branches': display_data, 'repo_url':repo_url}
		html = get_template('commitfollower/branch_choice_modal.html')
		return HttpResponse(html.render(Context(parameters)))
	except ObjectDoesNotExist:
		return HttpResponse(status=404)

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
			follower.add_remove_user_branches(request.user, repo_url, branch_names)
			return HttpResponse(status=200)
	else:
		return HttpResponse(status=501)


@login_required
def unfollow_repo(request, repo_url):
	"""
	Remove the repo and all of it's branches from the followed list for the user.
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
