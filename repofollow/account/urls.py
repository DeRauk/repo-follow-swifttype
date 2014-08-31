"""
url routing for the account app
"""

from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^login/$', views.Login.as_view(), name='login'),
	url(r'^logout/$', 'django.contrib.auth.views.logout',
                      {'next_page': '/'}, name='logout')
	)