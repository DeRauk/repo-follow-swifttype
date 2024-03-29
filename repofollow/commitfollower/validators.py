"""
Validations for the commitfollower app
"""

from __future__ import absolute_import
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urlparse import urlparse
from .models import Repository

UNSUPPORTED_VCS_PROVIDER_MSG = "Sorry, we currently only support repositories hosted on github.com"

def valid_url(url):
	"""
	Check to see if the input is a valid url.
	"""
	validate = URLValidator()
	try:
	    validate(url)
	except ValidationError:
		return False

	return True

def supported_vcs_provider(url):
	"""
	Check to see if the url is from a supported version control provider. (I.E. github.com)
	"""
	parsed = urlparse(url)
	vcs_provider = parsed.netloc
	if vcs_provider in [i[1] for i in Repository.REPO_CHOICES]:
		return True
	else:
		return False

def clean_url(url):
	if url[-1] == '/':
		return url[:-1]
	else:
		return url

def repo_contains_branches(repo_url, branch_name_list):
	if len(branch_name_list) == 0:
		return True
	repo = Repository.objects.get(url=repo_url)
	repo_branch_names = [b.name for b in repo.branch_set.all()]
	for branch_name in branch_name_list:
		if branch_name not in repo_branch_names:
			return False

	return True
