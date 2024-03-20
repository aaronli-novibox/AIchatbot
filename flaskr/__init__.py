import os
from flask import Flask, jsonify
from services.mongo import *
from bson import json_util

from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask import current_app, g
from .shp import get_shopify_api, extract_excel
from .db import get_mongo_db, close_db
# from config import config

# from .openai import get_openai_client


def config(app):

    load_dotenv()
    app.config["SHOPIFY_API_KEY"] = os.getenv("SHOPIFY_API_KEY")
    app.config["SHOPIFY_API_PASSWORD"] = os.getenv("SHOPIFY_API_PASSWORD")
    app.config["SHOPIFY_SHOP_NAME"] = os.getenv("SHOPIFY_SHOP_NAME")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["OPENAI_KEY"] = os.getenv("OPENAI_KEY")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        print(
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         'config/config.py'))
        app.config.from_pyfile(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'config/config.py'),
                               silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # config(app)

    @app.before_request
    def before_request():
        # if 'mongo' not in g:
        # print(app.config["MONGO_URI"])
        # g.mongo = PyMongo(app)
        # print(g.mongo.db.name)
        get_mongo_db()
        # get_shopify_api()
        # grandparent_dir = os.path.dirname(os.path.dirname(__file__))

        # extract_excel(
        #     os.path.join(grandparent_dir, "db_files/customers_export.xlsx"),
        #     'customers')
        # extract_excel(
        #     os.path.join(grandparent_dir, "db_files/orders_export_1.xlsx"),
        #     'orders')

    @app.after_request
    def after_request(response):
        close_db()
        return response

    @app.route('/products')
    def getProductsInfoFromMongoDB():
        products_cursor = getProductListFromMongoDB()
        products_list = list(products_cursor)

        return jsonify({
            'code': '0000',
            'data': {
                'products': products_list
            },
            'msg': 'success'
        })

    @app.route('/orders')
    def getOrdersInfoFromMongoDB():
        orders_cursor = getOrderListFromMongoDB()
        orders_list = list(orders_cursor)

        return jsonify({
            'code': '0000',
            'data': {
                'orders': orders_list
            },
            'msg': 'success'
        })

    @app.route('/customers')
    def getCustomersInfoFromMongoDB():
        customers_cursor = getCustomerListFromMongoDB()
        customers_list = list(customers_cursor)

        return jsonify({
            'code': '0000',
            'data': {
                'customers': customers_list
            },
            'msg': 'success'
        })

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
