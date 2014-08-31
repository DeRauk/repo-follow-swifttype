"""
Views for the commitfollower app
"""

from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def feed(request):
	context = RequestContext(request)
	return render_to_response('commitfollower/feed.html', context_instance=context)