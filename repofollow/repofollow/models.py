"""
Abstract models for use across apps
"""

from django.db import models
from django.conf import settings

class TimeStampedModel(models.Model):
  """
  An abstract base class model that provides self-updating ``created``
  and ``modified`` fields.
  """

  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  def __getattr__(self, attrname):
    """
    The database doesn't store time zone info, so we add it here
    """
    if attrname == 'created' or attrname == 'modified':
      date_time = super(TimeStampedModel, self).__getattr__(attrname)
      return date_time.replace(tzinfo=settings.TIME_ZONE_OBJ)
    else:
      return super(TimeStampedModel, self).__getattr__(attrname)

  class Meta:
    abstract = True
