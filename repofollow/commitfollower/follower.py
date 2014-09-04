"""
Controller logic for the commitfollower app
"""

from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urlparse
from requests_oauthlib import OAuth2Session
from datetime import datetime
from .models import Repository
from dateutil import parser as dateparser
import requests, logging, json, pdb

logger = logging.getLogger(__name__)

HEADERS = {'Accept': 'application/vnd.github.v3+json'}

def get_repo_branches(repo_url):
	"""
	Get the branches of a repository.
	"""

	follower = VcsWrapper(repo_url)
	follower.sync()


	return ""

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




class VcsWrapper:

	def __init__(self, repo_url):
		try:
			self.repo_url = repo_url

			parsed = urlparse(repo_url)
			self.repo_path = parsed.path

			self.follower = {
				'github.com': GithubFollower.get_instance(),
			}[parsed.netloc]
		except KeyError:
			raise ObjectDoesNotExist()

	def sync(self):
		""" Sync up the repository with our local database """

		try:
			repo = Repository.objects.get(url=self.repo_url)
		except Repository.DoesNotExist:
			self.initialize_new_repo()
			return

		now = datetime.now()

		# if we haven't reached last_updated_time + update_interval return early
		# next_sync_allowed = repo.synced + datetime.delta(0, repo.sync_interval_sec)
		if now < next_sync_allowed:
			return


		# grab the last updated time for the repo (from api)

		# if the updated time is less than our last updated time, return b/c nothing new
		# otherwise call sync_branches and sync_commits

		repo_updated_time = self.follower.get_last_updated(self.repo_path)
		branch_list = self.follower.get_branches(self.repo_path)
		commit_list = self.follower.get_commits(self.repo_path)

		repo.synced = now
		repo.save()

	def initialize_new_repo(self):
		None

	def sync_branches(self, repo_url, branch_list):
		None

	def sync_commits(self, repo_url, commit_list):
		None




def rate_limited(fn):
	"""
	A decorator to check if the api is rate limited and throw an exception if it
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
	sync_interval_sec = 600

	def __init__(self):
		self.client = OAuth2Session(self.properties['oauth_key'],
																	token=self.properties['oauth_token'])

	@rate_limited
	def get_last_updated(self, repo_path):
		"""
		Get when the repo was last pushed to
		"""
		url = "{}/repos{}".format(self.properties['api_url'], repo_path)
		headers = self.properties['request_headers']
		response = self.response_wrapper(self.client.get(url, headers=headers))

		resp_data = json.loads(response.text)
		updated_str = resp_data['updated_at']
		updated_time = dateparser.parse(updated_str)

		return updated_time

	@rate_limited
	def get_branches(self, repo_path):
		"""
		Use the Github REST api to get a list of branches for the repo_path
		"""
		headers = self.properties['request_headers']
		url = "{}/repos{}/branches".format(self.properties['api_url'], repo_path)
		response = self.response_wrapper(self.client.get(url, headers=headers))

		resp_data = json.loads(response.text)
		return [d['name'] for d in resp_data]

	@rate_limited
	def get_commits(self, repo_path):
		"""
		Use the Github REST api to get a list of commits for the repo_path
		"""
		commits = []
		headers = self.properties['request_headers']
		next_page = ''
		getMore = True
		url = "{}/repos{}/commits".format(self.properties['api_url'], repo_path)

		while getMore:
			response = self.response_wrapper(self.client.get(url, headers=headers))

			resp_data = json.loads(response.text)
			commits += [(d['sha'], d['commit']['message']) for d in resp_data]

			# Get next page by grabbing 'next' link if it exists, if not break
			links = response.headers['link'].split(',')
			try:
				next_page = [i for i in links if 'next' in i][0]
				url = next_page[next_page.rfind("<") + 1:next_page.rfind(">")]
			except IndexError:
				getMore = False

		return commits


	@staticmethod
	def response_wrapper(response):
		"""
		Handle some common checks and updates for github api responses
		"""
		if(response.status_code == 404):
			raise ObjectDoesNotExist()

		GithubFollower.update_rate_limit(response)
		return response


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

	@staticmethod
	def get_instance():
		if GithubFollower.instance == None:
			GithubFollower.instance = GithubFollower()

		return GithubFollower.instance
