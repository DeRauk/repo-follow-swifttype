"""
form classes for the account app
"""

from __future__ import absolute_import
from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
	"""
	Form class to clean the input coming from the login page.
	"""

	username = forms.CharField(widget=forms.TextInput( attrs={'class':'form-control',
															'placeholder': 'Username',
															'required': None,
															'autofocus': None}) )

	password = forms.CharField(widget=forms.PasswordInput( attrs={'class':'form-control',
																  'placeholder': 'Password',
																  'required': None}) )

	def clean(self):
		cleaned_data = super(LoginForm, self).clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		self.user = authenticate(username=username, password=password)
		if self.user is None:
			raise forms.ValidationError("Invalid username or password.")
		return cleaned_data
