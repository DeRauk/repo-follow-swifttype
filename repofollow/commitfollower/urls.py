"""
url routing for the commitfollower app
"""

from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^repos$', views.repo_list, name='list_repos'),
	url(r'^repos/remove/(?P<repo_url>.+)$', views.unfollow_repo, name='unfollow_repo'), # We'll validate the url later for better errors than 404
  url(r'^branches/update/(?P<repo_url>.+)$', views.update_branches, name='update_branches'),
	url(r'^branches/(?P<repo_url>.+)$', views.get_branches, name='get_branches'),
	# url(r'^branches/unfollow$', views.unfollow_branches, name='unfollow_branches'),
	)
