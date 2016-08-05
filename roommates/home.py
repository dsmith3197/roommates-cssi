from google.appengine.ext import ndb

class Home(ndb.Model):
	name = ndb.StringProperty(required = True)
	password = ndb.StringProperty(required = True)
	occupants = ndb.StringProperty(repeated = True)
	calendar_id = ndb.StringProperty()
#    stickies = #list of stickies with timestamps



