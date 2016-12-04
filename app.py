from flask import Flask
from flask_pymongo import PyMongo


class Settings:
	MONGO_HOST = 'db'


app = Flask(__name__)

app.config.from_object(Settings)
mongo = PyMongo(app)

print(app.extensions)


class Client:

	collection_name = 'clients'

	def __init__(self, username, first_name=None, last_name=None, **kwargs):
		self.username = username
		self.first_name = first_name
		self.last_name = last_name


	@classmethod
	def collection(cls):
		"""Returns flask_pymongo.wrappers.Collection.
		"""
		return mongo.db[cls.collection_name]

	def save(self, **kwargs):
		"""Saves a client in database or updates one if exists.
		"""
		doc = {
			'username': self.username,
			'firs_name': self.first_name,
			'last_name': self.last_name
		}
		
		if kwargs:
			doc.update(kwargs)
		return self.collection().update_one(
			{'username': self.username},
			    {'$set': 	
			    	{'username': self.username,
			    	 'first_name': self.first_name,
			    	 'last_name': self.last_name, }
			    }, 
		    upsert=True)

	@classmethod
	def get(cls, username):
		"""Returns a Client matching a username.
		"""
		doc = cls.collection().find_one({'username': username})
		if doc:
			return cls(**doc)
		else:
			return cls(username=None)

	def delete(self):
		"""Deletes a client matching a username."""
		return self.collection().delete_one({'username': self.username})



@app.route('/')
@app.route('/hello/<name>')
def index(name=None):
    if name:
        return 'Hello {}'.format(name)
    else:
        return 'Wellcome to our awersome site!!!'

@app.route('/client/save/<username>/<first_name>/<last_name>')
def client_save(username=None, first_name=None, last_name=None):
	if not username:
		return 'username required !!!'
	c = Client(username=username, 
               first_name=first_name, 
               last_name=last_name)
	c.save()
	return 'Client {}, {}, {} has been saved in database.'.format(
		c.username, c.first_name, c.last_name)

@app.route('/client/delete/<username>')
def client_delete(username=None):
	if not username:
		return 'username required !!!'
	c = Client(username=username)
	c.delete()
	return 'Client {} has been removed from database.'.format(
		c.username, c.first_name, c.last_name)

@app.route('/client/get/<username>')
def client_get(username=None):
	if not username:
		return 'username required !!!'
	c = Client.get(username=username)
	print(c.__dict__)
	return 'Client {}, {}, {} getted from database'.format(
		c.username, c.first_name, c.last_name)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
