"""
Simple application on Flask and Mongo to show basic example usage of
docker-compose service.
"""

from flask import Flask
from jinja2 import Template
from flask_pymongo import PyMongo


class Settings:
    """Configuration for Flask application and its extensions."""
    MONGO_HOST = 'db'


app = Flask(__name__)

app.config.from_object(Settings)
mongo = PyMongo(app)


class Client:
    collection_name = 'clients'

    def __init__(self, username, first_name=None, last_name=None, **kwargs):
        """Takes initial parameters for Client model.
        Parameters:
            username: necessary parameter used for identify client in database.
            first_name: client first name.
            last_name: client family name.
            kwargs: optional parameters which can be saved in same document
                where client will be saved.
        """
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        if kwargs:
            self._parameters = kwargs
        else:
            self._parameters = {}

    def __repr__(self):
        return '<Client username: {}, full_name: {} {}>'.format(
            self.username, self.first_name, self.last_name)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def collection(cls):
        """Returns flask_pymongo.wrappers.Collection."""
        return mongo.db[cls.collection_name]

    @classmethod
    def all(cls):
        """Returns pymongo cursor object with all clients from database."""
        return (cls(**client) for client in cls.collection().find({}))

    @classmethod
    def get(cls, username):
        """Returns a Client matching a username."""
        doc = cls.collection().find_one({'username': username})
        if doc:
            return cls(**doc)
        else:
            return cls(username=None)

    def save(self, **kwargs):
        """Saves a client in database or updates one if exists.
        Parameters:
            kwargs: put here parameters that must be saved in the same document.
                Take in mind this parameters will rewrite kwargs taken
                in __init__() method.
        """
        doc = {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
        if kwargs and self._parameters:
            doc.update(kwargs)
        elif self._parameters:
            doc.update(self._parameters)
            doc.update(kwargs)
        return self.collection().update_one(
            {'username': self.username},
            {'$set': doc},
            upsert=True)

    def delete(self):
        """Deletes a client matching a username."""
        return self.collection().delete_one({'username': self.username})


@app.route('/')
@app.route('/hello/<name>')
def index(name=None):
    if name:
        return 'Hello {}'.format(name)
    else:
        return 'Welcome to our awesome site!!!'


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
    return 'Client {}, {}, {} was taken from database'.format(
        c.username, c.first_name, c.last_name)


@app.route('/clients')
def get_all_clients():
    response = '<i><h4>List of all clients:</h4></i>'
    for counter, client in enumerate(Client.all(), 1):
        print(client)
        response += """
        <i><p style="margin-left:20px;">
            {}. Client: username: {}, full_name: {} {}
        </p></i>
        """.format(counter, client.username, client.first_name,
                   client.last_name)
    return Template(response).render()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
