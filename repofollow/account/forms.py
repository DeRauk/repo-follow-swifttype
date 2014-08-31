"""
form classes for the account app
"""

from __future__ import absolute_import
from django import forms
from django.contrib.auth import authenticate
import pdb

class LoginForm(forms.Form):
	"""
	Form class to clean the input coming from the login page.
	"""

	email = forms.CharField(widget=forms.TextInput( attrs={'class':'form-control',
															'placeholder': 'Username',
															'required': None,
															'autofocus': None}) )

	password = forms.CharField(widget=forms.PasswordInput( attrs={'class':'form-control',
																  'placeholder': 'Password',
																  'required': None}) )

	def clean(self):
		cleaned_data = super(LoginForm, self).clean()
		email = cleaned_data.get('email')
		password = cleaned_data.get('password')
		self.user = authenticate(username=email, password=password)
		pdb.set_trace()
		if self.user is None:
			raise forms.ValidationError("Invalid email or password.")
		return cleaned_data
