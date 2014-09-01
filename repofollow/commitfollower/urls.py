"""
url routing for the commitfollower app
"""

from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^repos$', views.repo_list, name='list_repos'),
	url(r'^repos/remove/(?P<repo_url>.+)$', views.unfollow_branches, name='remove_repo'), # We'll validate the url later for better errors than 404
	url(r'^branches/(?P<repo_url>.+)$', views.get_branches, name='get_branches'),
	url(r'^branches/follow$', views.follow_branches, name='follow_branches'),
	url(r'^branches/unfollow$', views.unfollow_branches, name='unfollow_branches'),
	)