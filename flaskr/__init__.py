import os
from flask import Flask, jsonify, request, abort
from services.mongo import *
from services.aichatbot.AIchatBotService import *
from services.mongo.MongoService import *
from bson import json_util

from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask import current_app, g
from .shp import *
from .oai import *
from .db import get_mongo_db, close_db
from services.webhook.webhookService import *
import hmac
import hashlib
import base64

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

    # router
    @app.before_request
    def before_request():

        # connect to mongodb
        get_mongo_db()
        get_openai_service()

        # path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
        #                     "db_files/orders_export_1.xlsx")

        # path2 = os.path.join(os.path.dirname(os.path.dirname(__file__)),
        #                      "db_files/customers_export.xlsx")

        # extract_excel(path, "orders")
        # extract_excel(path2, "customers")

        # shopify_class = shoipfy_services()
        # shopify_class.query("products")

        # del shopify_class

    @app.after_request
    def after_request(response):
        close_db()
        close_openai_service()
        # import gc
        # gc.collect()    # 强制执行垃圾收集
        # print("garbage", gc.garbage)    # 打印无法回收的对象列表

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

    @app.route('/influencers')
    def getInfluencersInfoFromMongoDB():
        influencers_cursor = getInfluencerListFromMongoDB()
        influencers_list = list(influencers_cursor)

        return jsonify({
            'code': '0000',
            'data': {
                'influencers': influencers_list
            },
            'msg': 'success'
        })

    @app.route('/')
    def hello_novi_box():
        return "hello novi box"

    # aichatbot service
    @app.route('/user-typing', methods=['POST'])
    def user_typing():
        req = request.json
        return userTyping(req)

    @app.route('/recommand-list', methods=['POST'])
    def recommand_by_list():
        req = request.json
        return recommandGiftByList(req)

    @app.route('/recommand-user-typing', methods=['POST'])
    def recommand_by_user_typing():
        req = request.json
        return recommandGiftByUserInput(req)

    def verify_webhook(data, hmac_header):
        digest = hmac.new(app.config['SHOPIFY_API_PASSWORD'].encode('utf-8'),
                          data,
                          digestmod=hashlib.sha256).digest()
        computed_hmac = base64.b64encode(digest)

        return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

    @app.route('/webhook', methods=['POST'])
    def handle_webhook():
        data = request.get_data()
        verified = verify_webhook(data,
                                  request.headers.get('X-Shopify-Hmac-SHA256'))

        if not verified:
            abort(401)

        # Process webhook payload

        webhookService(data)

    return ('', 200)


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
