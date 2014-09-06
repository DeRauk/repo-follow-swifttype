"""
url routing for the repofollow app (main url router)
"""

from django.conf.urls import patterns, include, url
from django.conf import settings
from commitfollower.views import feed
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^account/', include('account.urls', namespace='account')),
	  url(r'^$', feed), # Map the index to the commit feed
    url(r'^follower/', include('commitfollower.urls', namespace='follower')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
