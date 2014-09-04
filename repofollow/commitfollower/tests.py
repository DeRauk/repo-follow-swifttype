from django.test import TestCase
from django.conf import settings
from follower import GithubFollower
import requests

class GithubConnectionTest(TestCase):
  def setUp(self):
    None

  def test_can_connect_to_github(self):
    resp = requests.get("https://api.github.com")
    self.assertEqual(resp.status_code, 200)

class GithubOauthConnectionTest(TestCase):
  def setup(self):
    None

  def test_oauth_authenticated_to_github(self):
    follower = GithubFollower.get_instance()
    client = follower.client
    resp = client.get("https://api.github.com/users/octocat/orgs")
    rate_limit = int(resp.headers['X-RateLimit-Limit'])
    self.assertEqual(rate_limit, 5000)
