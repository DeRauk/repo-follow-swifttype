repo-follow-swifttype
=====================

# Setup
I used postgres as a backend persistent store and memcached as my cache.  Both of these will need to be installed.

### Postgres
The postgres settings can be found at /repofollow/repofollow/settings.py on line 121. You'll need to update the user, password, schema name, and possibly host and port.

### Memcached
The Memcached settings can be found at /repofollow/repofollow/settings.py on line 88. You might need to change the host on port, I have them set as the default.

### Python libraries
1. If you're using virtualenv, start a new virtual environment and activate it.
2. Install everything in the requirements file at /docs/requirements.txt with pip. `pip install -r requirements.txt`
