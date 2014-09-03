"""
models for the commitfollower app
"""

from django.db import models
from repofollow.models import TimeStampedModel
from django.conf import settings


class Repository(TimeStampedModel):
    """
    Model representing a source code repository
    """

    # To allow expansion to bitbucket or some other hip, new, up and coming site
    # The descriptive name here should be the netloc for the vcs site to be
    # validated
    GITHUB = 0
    REPO_CHOICES = (
        (GITHUB, "github.com"),
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


class Commit(TimeStampedModel):
    """
    Model representing a commit for a branch
    """

    number = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    branch = models.ForeignKey(Branch)
    message = models.TextField(null=True)
    added = models.DateTimeField()

    class Meta:
        db_table = "commits"

    def __unicode__(self):
        return "{}\n{}\n{}".format(str(self.branch), self.added, self.message)
