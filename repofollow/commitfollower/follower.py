"""
Controller logic for the commitfollower app
"""

from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urlparse
from requests_oauthlib import OAuth2Session
from datetime import datetime
import requests, logging, pdb

logger = logging.getLogger(__name__)

HEADERS = {'Accept': 'application/vnd.github.v3+json'}

def get_repo_branches(repo_url):
	"""
	Get the branches of a repository.
	"""

	parsed = urlparse(repo_url)
	repo_path = parsed.path
	follower = get_vcs_api(parsed.netloc)
	return follower.get_branches(repo_path)

	# If we have the url in our db just grab the urls and return them


	# Otherwise, figure out which apis to use based on url and call them
	# put the returned branches in the database and then return them from the function

	None

def unlink_user_branch(user, branch_id):
	"""
	Have a user stop following a branch
	"""
	# Remove the user from the m2m relation in branches
	None

def link_user_branch(user, branch_id):
	"""
	Have a user start following a branch
	"""
	None

def get_recent_commits(user, num):
	"""
	Get the last `num` commits for a user's branches
	"""
	None


class RateLimitException(Exception):
	"""
	Raised when a oauth api has reached it's rate limit

	Attributes:
		reset_time -- when the rate limit will reset
		api -- which api threw the exception
		msg -- details about the exception
	"""

	def __init__(self, reset_time, api, msg=""):
		self.reset_time = reset_time
		self.api = api
		self.msg = msg




def rate_limited(fn):
	"""
	A decorator to check if the class is rate limited and throw an exception if it
	is.
	"""
	def check_limited(self, *argv, **kwargs):
		if self.limited:
			now = datetime.now()
			reset = self.limit_reset
			if now < reset:
				raise RateLimitException(reset, self.site_key)
			else:
				self.limited = False
		return fn(self, *argv, **kwargs)
	return check_limited


class GithubFollower:
	"""
	A follower class for the github api. Meant to be used as a singleton.

	Attributes:
		instance -- singleton instance for the class
		site_key -- identifier for github for the api factory
		properties -- configuration properties for github
		limited -- boolen, true if the api is currently limited
		limit_reset -- datetime of when the api will no longer be limited
	"""
	instance = None
	site_key = 'github.com'
	properties = settings.VCS_PROPERTIES[site_key]
	limited = False
	limit_reset = None

	def __init__(self):
		self.client = OAuth2Session(self.properties['oauth_key'],
																	token=self.properties['oauth_token'])

	@rate_limited
	def get_branches(self, repo_path):
		""" Get the branches for a repository from the site api """
		url = "{}/repos{}".format(self.properties['api_url'], repo_path)
		headers = self.properties['request_headers']
		response = self.update_rate_limit(self.client.get(url, headers=headers))
		return response.text

	@rate_limited
	def sync(self, repo_path):
		None

	@staticmethod
	def update_rate_limit(response):
		"""
		Updates the rate limit from the response headers.
		"""
		remaining = int(response.headers['x-ratelimit-remaining'])
		reset_ms = int(response.headers['x-ratelimit-reset'])
		reset = datetime.fromtimestamp(reset_ms)
		logger.info("Remaining rate limit: " + str(remaining))

		if remaining == 0:
			GithubFollower.limited = True
			GithubFollower.limit_reset = reset
			raise RateLimitException(reset, GithubFollower.site_key)
		return response

	@staticmethod
	def get_instance():
		if GithubFollower.instance == None:
			GithubFollower.instance = GithubFollower()

		return GithubFollower.instance


def get_vcs_api(site):
	try:
		return {
			'github.com': GithubFollower.get_instance(),
		}[site]
	except KeyError:
		raise ObjectDoesNotExist()
