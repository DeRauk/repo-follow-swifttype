"""
views for the account app
"""

from __future__ import absolute_import
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth import login
from django.views.generic import View
from .forms import LoginForm
import logging

logger = logging.getLogger(__name__)

class Login(View):
	def get(self, request):
		context = RequestContext(request, {'request': request,
			                            	'user': request.user})

		if not request.user.is_anonymous():
			return redirect("/")
		form = LoginForm()
		return render_to_response('account/login.html', {'form': form},
   									context_instance=context)
	def post(self, request):
		context = RequestContext(request,
                           {'request': request,
                            'user': request.user})

		form = LoginForm(request.POST)
		if form.is_valid():
			login(request, form.user)
			return redirect("/")
		else:
			return render_to_response('account/login.html', {'form': form}, 
											context_instance=context)
