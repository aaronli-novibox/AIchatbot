import os
from flask import Flask, jsonify, request
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

        # json_data = [
        #     {
        #         "influencer_name":
        #             "Buse Keskin",
        #         "influencer_email":
        #             "healthykitchenohio@gmail.com",
        #         "promo_code":
        #             "BUSEK10",
        #         "contract_start":
        #             "02-18-2024",
        #         "contract_end":
        #             "02-18-2025",
        #         "product": [{
        #             "product_sku": "BAL2308020W",
        #             "product_name": "File Night Light white",
        #             "commission": "15%",
        #             "product_contract_start": "02-18-2024",
        #             "product_contract_end": "02-18-2025"
        #         }]
        #     },
        #     {
        #         "influencer_name":
        #             "Rachel Koehler",
        #         "influencer_email":
        #             "heart4ocr@gmail.com",
        #         "promo_code":
        #             "RACHELK10",
        #         "contract_start":
        #             "02-16-2024",
        #         "contract_end":
        #             "02-16-2025",
        #         "product": [{
        #             "product_sku": "BAL2308019W",
        #             "product_name": "File Night mini Lamp white",
        #             "commission": "15%",
        #             "product_contract_start": "02-16-2024",
        #             "product_contract_end": "02-16-2025"
        #         }]
        #     },
        #     {
        #         "influencer_name":
        #             "Melinda Ly",
        #         "influencer_email":
        #             "businessmelly96@gmail.com",
        #         "promo_code":
        #             "MELINDAL10",
        #         "contract_start":
        #             "02-16-2024",
        #         "contract_end":
        #             "02-16-2025",
        #         "product": [{
        #             "product_sku": "BGS2308010B",
        #             "product_name": "Sirius P5Earbuds",
        #             "commission": "13%",
        #             "product_contract_start": "02-16-2024",
        #             "product_contract_end": "02-16-2025",
        #         }, {
        #             "product_sku": "BCT2308014L",
        #             "product_name": "Mini Plunger-shaped Diffuser(Leather)",
        #             "commission": "22%",
        #             "product_contract_start": "02-16-2024",
        #             "product_contract_end": "02-16-2025",
        #         }]
        #     },
        #     {
        #         "influencer_name":
        #             "Hani Mak",
        #         "influencer_email":
        #             "hanigracework@gmail.com",
        #         "promo_code":
        #             "HANIK10",
        #         "contract_start":
        #             "02-16-2024",
        #         "contract_end":
        #             "02-16-2025",
        #         "product": [{
        #             "product_sku": "BAL2308018W",
        #             "product_name": "Fila Night Desk Lamp white",
        #             "commission": "15%",
        #             "product_contract_start": "02-16-2024",
        #             "product_contract_end": "02-16-2025"
        #         }]
        #     },
        #     {
        #         "influencer_name":
        #             "Jessica west",
        #         "influencer_email":
        #             "collabwjess@gmail.com",
        #         "promo_code":
        #             "JESSICAW10",
        #         "contract_start":
        #             "02-16-2024",
        #         "contract_end":
        #             "02-16-2025",
        #         "product": [{
        #             "product_sku": "BAL2308018W",
        #             "product_name": "Fila Night Desk Lamp white",
        #             "commission": "15%",
        #             "product_contract_start": "02-16-2024",
        #             "product_contract_end": "02-16-2025"
        #         }]
        #     },
        #     {
        #         "influencer_name":
        #             "Cassandra Farley",
        #         "influencer_email":
        #             None,
        #         "promo_code":
        #             "CASSANDRAF10",
        #         "contract_start":
        #             "03-01-2024",
        #         "contract_end":
        #             "03-01-2025",
        #         "product": [{
        #             "product_sku": "BGS2308010B",
        #             "product_name": "Sirius P5Earbuds",
        #             "commission": "13%",
        #             "product_contract_start": "03-01-2024",
        #             "product_contract_end": "03-01-2025"
        #         }]
        #     },
        #     {
        #         "influencer_name": "TrackerTest1",
        #         "influencer_email": None,
        #         "promo_code": "NOVIBOX20",
        #         "contract_start": None,
        #         "contract_end": None,
        #         "product": []
        #     },
        #     {
        #         "influencer_name": "TrackerTest2",
        #         "influencer_email": None,
        #         "promo_code": "UGC",
        #         "contract_start": None,
        #         "contract_end": None,
        #         "product": []
        #     },
        #     {
        #         "influencer_name": "TrackerTest3",
        #         "influencer_email": None,
        #         "promo_code": "WELCOME10",
        #         "contract_start": None,
        #         "contract_end": None,
        #         "product": []
        #     },
        # ]
        # insertInfluencerData(json_data)

        # shopify_class = shoipfy_services()
        # shopify_class.query("products")

        # del shopify_class

    @app.after_request
    def after_request(response):
        close_db()
        close_openai_service()
        import gc
        gc.collect()    # 强制执行垃圾收集
        print("garbage", gc.garbage)    # 打印无法回收的对象列表

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
        return "hello_novi_box"

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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
