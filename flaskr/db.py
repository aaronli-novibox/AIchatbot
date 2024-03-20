from pymongo import MongoClient
from flask import current_app, g


# connect with openai service
def get_mongo_db():

    if 'db' not in g:
        g.db = MongoClient(current_app.config['MONGO_URI'])

    return g.db


# disconnect with mongoDB
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
