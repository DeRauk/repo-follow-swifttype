"""
Controller logic for the commitfollower app
"""

from __future__ import absolute_import
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urlparse
from requests_oauthlib import OAuth2Session
from datetime import timedelta, datetime
from .models import Repository, Branch, Commit
from dateutil import parser as dateparser
from dateutil import tz
import requests, logging, json, pdb

logger = logging.getLogger(__name__)

HEADERS = {'Accept': 'application/vnd.github.v3+json'}

def get_repo_branches(user, repo_url):
	"""
	Get the branches of a repository.
	"""

	follower = VcsWrapper(user, repo_url)
	follower.sync()

	repo = follower.repo

	return repo.branch_set.all()

def get_user_repos(user):
	return Repository.objects.filter(branch__followers=user)

def add_remove_user_branches(user, repo_url, submitted_branch_names):
	try:
		repo = Repository.objects.get(url=repo_url)
		repo_branches = repo.branch_set.all()
		user_branches = user.branch_set.filter(repository=repo)
		user_branch_names = [ubranch.name for ubranch in user_branches]


		new_branches = [branch for branch in repo_branches if branch.name in \
											submitted_branch_names and branch.name not in \
												user_branch_names]

		deleted_branches = [branch for branch in repo_branches if branch.name in \
													user_branch_names and branch.name not in \
														submitted_branch_names]

		for branch in deleted_branches:
			branch.followers.remove(user)

		for branch in new_branches:
			branch.followers.add(user)


	except Repository.DoesNotExist:
		raise ObjectDoesNotExist()

def get_recent_commits(user, num):
	"""
	Get the last `num` commits for a user's branches
	"""



	# follower = VcsWrapper(user, repo_url)
	# follower.sync()
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

	def __init__(self, user, repo_url):
		try:
			self.repo = None
			self.user = user
			self.repo_url = repo_url

			parsed = urlparse(repo_url)
			self.repo_path = parsed.path

			self.follower = {
				'github.com': GithubFollower.get_instance(),
			}[parsed.netloc]

		except KeyError:
			raise ObjectDoesNotExist()

	def should_sync(self, repo):
		now = datetime.now(tz.gettz(settings.TIME_ZONE))

		# A minimum required amount of time betwen calls helps with rate limiting
		time_interval = timedelta(0, self.follower.properties['sync_interval_sec'])
		next_sync_allowed = repo.synced_with_tz() + time_interval
		if now < next_sync_allowed:
			logger.debug("Too early to allow another sync")
			return False

		# if the remote updated time is less than our last updated time,
		# return b/c there's nothing new to sync
		remote_updated_time = self.follower.get_last_updated(self.repo_path)
		local_updated_time = repo.synced_with_tz()

		if local_updated_time >= remote_updated_time:
			logger.debug("Remote hasn't been updated")
			return False

		return True



	def sync(self):
		""" Sync up the repository with our local database """

		try:
			self.repo = Repository.objects.get(url=self.repo_url)
		except Repository.DoesNotExist:
			self.initialize_new_repo()
			return

		if not self.should_sync(self.repo):
			return


		remote_branch_list = self.follower.get_branches(self.repo_path)
		local_branch_list  = [b.name for b in self.repo.branch_set.all()]
		new_branches = [r for r in remote_branch_list if r not in local_branch_list]
		stale_branches = [l for l in local_branch_list if l not in remote_branch_list]

		if len(stale_branches) > 0:
			for branch in self.repo.branch_set.all():
				if branch.name in stale_branches:
					branch.delete()

		if len(new_branches) > 0:
			for branch_name in new_branches:
				self.add_branch(branch_name)

		## Add any new commits to previously existing branches
		self.sync_branches([l for l in self.repo.branch_set.all() \
																	if l.name not in new_branches])

		now = datetime.now(tz.gettz(settings.TIME_ZONE))
		self.repo.synced = now
		self.repo.save()

	def initialize_new_repo(self):
		self.repo = Repository(url=self.repo_url, type=self.follower.vcs,
												source=self.follower.source)
		self.repo.save()

		branch_list = self.follower.get_branches(self.repo_path)
		for branch_name in branch_list:
			self.add_branch(branch_name)

	def sync_branches(self, branches):
		"""
		Add commits newer than our newest commit in the local db
		"""
		for branch in branches:
			most_recent = branch.commit_set.order_by("-added").first()
			last_committed_date = most_recent.added.replace(tzinfo=settings.TIME_ZONE_OBJ)
			commit_list = self.follower.get_commits(self.repo_path, branch.name,
											most_recent.added + timedelta(hours=-7)) #B/c Github subtracted 7 hours?
			for commit_data in commit_list:
				if commit_data[3] > last_committed_date:
					commit = Commit.create(branch, *commit_data)
					commit.save()


	def add_branch(self, name):
		branch = Branch.create(self.repo, name)
		branch.save()

		commit_list = self.follower.get_commits(self.repo_path, branch.name)
		for commit_data in commit_list:
			commit = Commit.create(branch, *commit_data)
			commit.save()



def rate_limited(fn):
	"""
	A decorator to check if the api is rate limited and throw an exception if it
	is.
	"""
	def check_limited(self, *argv, **kwargs):
		if self.limited:
			now = datetime.now(tz.gettz(settings.TIME_ZONE))
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
	site_key = 'github.com'
	source = Repository.GITHUB
	vcs  = Repository.GIT
	properties = settings.VCS_PROPERTIES[site_key]
	limited = False
	limit_reset = None

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
		updated_str = resp_data['pushed_at']
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
	def get_commits(self, repo_path, branch, since=None):
		"""
		Use the Github REST api to get a list of commits for the repo_path.
		Returns [(author, sha, msg, date)]
		"""
		commits = []
		headers = self.properties['request_headers']
		url = "{}/repos{}/commits?sha={}".format(self.properties['api_url'],
																									repo_path, branch)
		if since is not None:
			since_param = since.replace(microsecond=0).\
													replace(tzinfo=None).isoformat()
			url = "{}&since={}".format(url, since_param)

		while url is not None:
			response = self.response_wrapper(self.client.get(url, headers=headers))
			resp_data = json.loads(response.text)
			commits += [(d['commit']['author']['name'],
										d['sha'],
										  d['commit']['message'], \
												dateparser.parse(d['commit']['author']['date'])\
													.replace(tzinfo=settings.TIME_ZONE_OBJ)) \
									for d in resp_data]

			# Get next page by grabbing 'next' link if it exists
			if 'link' in response.headers and 'next' in response.headers['link']:
				links = response.headers['link'].split(',')
				next_page_list = [i for i in links if 'next' in i]

				if len(next_page_list) > 0:
					next_page = next_page_list[0]
					url = next_page[next_page.rfind("<") + 1:next_page.rfind(">")]
				else:
					url = None
			else:
				url = None

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
		if not hasattr(GithubFollower, 'instance'):
			GithubFollower.instance = GithubFollower()

		return GithubFollower.instance
