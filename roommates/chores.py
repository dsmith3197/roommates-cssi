from google.appengine.ext import ndb

class Chore(ndb.Model):
	chore_name = ndb.StringProperty(required = True)
	workers = ndb.StringProperty(repeated = True)
	workers_names = ndb.StringProperty(repeated = True)
	index = ndb.IntegerProperty(default= 0)
	end_time = ndb.FloatProperty(required=True)
	duration = ndb.FloatProperty(required=True)
	completed = ndb.BooleanProperty(default=False) 
	home_key = ndb.KeyProperty(kind = 'Home')