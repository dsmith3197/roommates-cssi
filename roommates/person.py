from google.appengine.ext import ndb
from google.appengine.api import users


class Person(ndb.Model):
    user_id = ndb.StringProperty()
    name = ndb.StringProperty(required = True)
    phone_number = ndb.IntegerProperty(required = True)
    home_key = ndb.KeyProperty(kind = 'Home')
    calendar_id = ndb.StringProperty()
    location = ndb.BooleanProperty(default=False) #True if in room; False if out of room
    do_not_disturb = ndb.BooleanProperty(default=False) #True if on; False if off

    color = ndb.StringProperty(required=True)
    email_address = ndb.StringProperty(required=True)
