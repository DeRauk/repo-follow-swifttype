"""
models for the commitfollower app
"""

from django.db import models
from repofollow.models import TimeStampedModel
from django.conf import settings
from datetime import datetime

GITHUB_DOMAIN = "github.com"

class Repository(TimeStampedModel):
  """
  Model representing a source code repository
  """

  # To allow expansion to bitbucket or some other hip, new, up and coming site
  # The descriptive name here should be the netloc for the vcs site to be
  # validated
  GITHUB = 0
  REPO_CHOICES = (
      (GITHUB, GITHUB_DOMAIN),
  )

  # Obviously a lot more would need to be done to expand to another source control
  # engine such as svn, but I didn't think it hurt to specify which type of source control
  # backed a repository
  GIT = 0
  SOURCE_CONTROL_CHOICES = (
      (GIT, "Git"),
  )

  url = models.CharField(max_length=100, primary_key=True)
  type = models.IntegerField(choices=SOURCE_CONTROL_CHOICES)
  source = models.IntegerField(choices=REPO_CHOICES)
  synced = models.DateTimeField(auto_now_add=True)

  def synced_with_tz(self):
  	return self.synced.replace(tzinfo=settings.TIME_ZONE_OBJ)

  def get_name(self):
      return {
        Repository.GITHUB: self.url.split("/")[-1]
      }[self.type]

  class Meta:
      db_table = "repositories"

  def __unicode__(self):
      return self.url


class Branch(TimeStampedModel):
    """
    Model representing a branch of a repository
    """

    repository = models.ForeignKey(Repository)
    name = models.CharField(max_length=50)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = "branches"

    def __unicode__(self):
        return "{} - {}".format(str(self.repository), self.name)

    @classmethod
    def create(cls, repository, name):
    	return cls(repository=repository, name=name)

    def get_url(self):
      return {
        Repository.GITHUB: "{}/tree/{}".format(self.repository.url, self.name)
      }[self.repository.type]


    def save(self, *args, **kwargs):
    	"""
    	Make sure the repository updated time is set
    	"""
    	self.repository.updated = datetime.now()
    	self.repository.save()
    	super(Branch, self).save(*args, **kwargs)


class Commit(TimeStampedModel):
    """
    Model representing a commit for a branch
    """

    sha = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    branch = models.ForeignKey(Branch)
    message = models.TextField(null=True)
    added = models.DateTimeField()
    author_image_url = models.CharField(max_length=100, null=True)

    @classmethod
    def create(cls, branch, author, sha, message, date, image_url):
    	return cls(branch=branch, author=author, sha=sha,
    								message=message, added=date, author_image_url=image_url)

    def save(self, *args, **kwargs):
    	"""
    	Make sure the repository updated time is set
    	"""
    	self.branch.repository.updated = datetime.now()
    	self.branch.repository.save()
    	super(Commit, self).save(*args, **kwargs)

    def info_is_equal(self, other_commit):
      """
      True if the only difference between these commits is the branch they're on
      """
      if self.branch.repository == other_commit.branch.repository and \
        self.sha == other_commit.sha:
        return True
      else:
        return False

    def get_author_link(self):
      return {
        Repository.GITHUB: "https://{}/{}".format(GITHUB_DOMAIN,self.author)
      }[self.branch.repository.type]

    def get_original_link(self):
      return {
        Repository.GITHUB: "{}/commit/{}".format(self.branch.repository.url,self.sha)
      }[self.branch.repository.type]

    class Meta:
        db_table = "commits"

    def __unicode__(self):
        return "{}\n{}\n{}".format(str(self.branch), self.added, self.message)
