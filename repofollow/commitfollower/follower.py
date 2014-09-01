"""
Controller logic for the commitfollower app
"""

from __future__ import absolute_import


def get_repo_branches(repo_url):
	"""
	Get the branches of a repository.
	"""

	# If we have the url in our db just grab the urls and return them

	# Otherwise, figure out which apis to use based on url and call them
	# put the returned branches in the database and then return them from the function

	None

def unlink_user_branch(user, branch_id):
	"""
	Have a user stop following a branch
	"""
	# Remove the user from the m2m relation in branches
	None

def link_user_branch(user, branch_id):
	"""
	Have a user start following a branch
	"""
	None

def get_recent_commits(user, num):
	"""
	Get the last `num` commits for a user's branches
	"""
	None