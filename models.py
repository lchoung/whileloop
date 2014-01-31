from google.appengine.ext import ndb

class User(ndb.Model):
	user_id = ndb.StringProperty(required = True)
	tags = ndb.StringProperty(repeated = True)

class Task(ndb.Model):
	author = ndb.UserProperty(required = True)
	task = ndb.StringProperty(required = True, indexed = False)
	duedate = ndb.DateTimeProperty(required = False)
	tag = ndb.StringProperty(required = True)

class Tag(ndb.Model):
	tag = ndb.StringProperty(required = True)