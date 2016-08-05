from google.appengine.ext import ndb

class Sticky(ndb.Model):
    title = ndb.StringProperty(required = True)
    content = ndb.StringProperty(required = True)  
    author = ndb.StringProperty(required = False)  #defined by user_id
    home_key = ndb.KeyProperty(kind = 'Home')
    important = ndb.BooleanProperty(default=False)
    completed = important = ndb.BooleanProperty(default=False)
    time_created = ndb.DateTimeProperty(auto_now=True)
    expiration = ndb.FloatProperty(required=True)