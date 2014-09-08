from django.core.management.base import NoArgsCommand, make_option
from django.contrib.auth.models import User

class Command(NoArgsCommand):
  help = "Setup the database with the initial users. Run after syncdb."
  option_list= NoArgsCommand.option_list + (
    make_option('--verbose', action='store_true'),
  )

  def handle_noargs(self, **options):
    user = User.objects.create_user('derauk', 'derauk@gmail.com', 'derauk')
    print("Creating user derauk!")
    user.save()

    user = User.objects.create_user('swifttype', 'swift@type.com', 'swifttype')
    print("Creating user swifttype!")
    user.save()
