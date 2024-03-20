from openai import OpenAI
from flask import current_app, g


# connect with openai service
def get_openai_service():

    if 'clientOpenAI' not in g:
        g.clientOpenAI = OpenAI(api_key=current_app.config['OPENAI_KEY'])

    return g.clientOpenAI


# # disconnect with mongoDB
# def close_db(e=None):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()
