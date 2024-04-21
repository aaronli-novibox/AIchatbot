import os
from flask import Flask, jsonify, request
from services.mongo import *
from services.aichatbot.AIchatBotService import *
from services.mongo.MongoService import *
from bson.objectid import ObjectId
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_cors import CORS

from flask_pymongo import PyMongo
from dotenv import load_dotenv
from flask import current_app, g
from flaskr.shp import *
from flaskr.oai import *
from flaskr.db import get_mongo_db, close_db

# from config import config

# from .openai import get_openai_client


# 假设这是你加载模型的函数
def load_model():
    # 加载模型
    emb_model = FlagModel(os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'services/aichatbot/models/models--BAAI--bge-large-zh-v1.5/snapshots/c11661ba3f9407eeb473765838eb4437e0f015c0'
    ),
                          query_instruction_for_retrieval="为这个句子生成表示以用于检索商品：",
                          use_fp16=True)
    return emb_model


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # Browser allows cross-domain requests from specific origins
    CORS(app)
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

    app.config['MODEL'] = load_model()

    # router
    @app.before_request
    def before_request():

        # connect to mongodb
        get_mongo_db()
        get_openai_service()

        # insertInfluencerData(json_data)

        # shopify_class = shoipfy_services()
        # shopify_class.query("products")

        # del shopify_class

    @app.after_request
    def after_request(response):
        close_db()
        close_openai_service()

        return response

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        influencer_email = data.get('influencer_email')
        password = data.get('password')

        # Check if influencer_name or influencer_email already exists
        influencers_collection = getNewInfluencerListFromMongoDB()
        existing_user = influencers_collection.find_one({
            '$or': [{
                'influencer_name': influencer_name
            }, {
                'influencer_email': influencer_email
            }]
        })
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Hash password
        hashed_password = generate_password_hash(password,
                                                 method='pbkdf2:sha256')

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        # Save user to database
        # influencers_collection.insert_one({
        #     'influencer_name': influencer_name,
        #     'influencer_email': influencer_email,
        #     'password': hashed_password,
        #     'verification_token': verification_token
        # })

        return jsonify({
            'message': 'User registered successfully',
            'role': 'editor'
        }), 201

    # Login
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        influencer_identifier = data.get('email') or data.get('promocode')
        password = data.get('password')

        influencers_collection = getNewInfluencerListFromMongoDB()
        # Find user by influencer_name or influencer_email
        user = influencers_collection.find_one({
            '$or': [{
                'promo_code': influencer_identifier
            }, {
                'influencer_email': influencer_identifier
            }]
        })
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check password
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid password'}), 401

        # Convert MongoDB documents to a JSON serializable format
        user_data = {
            k: str(v) if isinstance(v, ObjectId) else v
            for k, v in user.items()
        }

        return jsonify({'message': 'Login successful', 'user': user_data}), 200

    @app.route('/username', methods=['POST'])
    def generate_username():
        data = request.get_json()
        first = data.get('firstname')
        last = data.get('lastname')
        encode = (last[0].upper() + first[0].upper()).strip()

        req = 'influencers'    # 'products' / 'customers
        url = f'https://back.noviboxweb.com/{req}'

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data["code"] == '0000':
                data = data['data'][req]

            else:
                data = None
                print("Bad request")
        else:
            print(
                f"Error: Unable to fetch data. Status code: {response.status_code}"
            )

        username = [
            promo['promo_code'].replace(encode, "")
            for promo in data
            if promo['promo_code'].startswith(encode)
        ]

        return jsonify({
            'message': 'Generate successful',
            'promocode': encode
        }), 200

    @app.route('/promocode', methods=['POST'])
    def promo_generator():
        data = request.get_json()
        first = data.get('firstname')
        last = data.get('lastname')
        encode = (last[0].upper() + first[0].upper()).strip() + '_NOVIBOX_'

        req = 'influencers'    # 'products' / 'customers
        url = f'https://back.noviboxweb.com/{req}'

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data["code"] == '0000':
                data = data['data'][req]

            else:
                data = None
                print("Bad request")
        else:
            print(
                f"Error: Unable to fetch data. Status code: {response.status_code}"
            )

        promo_codes = [
            promo['promo_code'].replace(encode, "")
            for promo in data
            if promo['promo_code'].startswith(encode)
        ]
        if promo_codes:
            encode = encode + str(sorted(list(map(int, promo_codes)))[-1] + 1)
        else:
            encode = encode + "1"

        return jsonify({
            'message': 'Generate successful',
            'promocode': encode
        }), 200

    @app.route('/updatepromocode', methods=['POST'])
    def promo_change():
        data = request.get_json()
        encode = data.get('promocode')

        req = 'influencers'    # 'products' / 'customers
        url = f'https://back.noviboxweb.com/{req}'

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data["code"] == '0000':
                data = data['data'][req]

            else:
                data = None
                print("Bad request")
        else:
            print(
                f"Error: Unable to fetch data. Status code: {response.status_code}"
            )
        promo_codes = [
            promo['promo_code'].replace(encode, "")
            for promo in data
            if promo['promo_code'].startswith(encode)
        ]
        if promo_codes:
            encode = encode + str(sorted(list(map(int, promo_codes)))[-1] + 1)
        else:
            encode = encode + "1"

        return jsonify({
            'message': 'Update successful',
            'promocode': encode
        }), 200

    # Forgot password endpoint
    @app.route('/forgot_password', methods=['POST'])
    def forgot_password():
        data = request.get_json()
        influencer_email = data.get('influencer_email')

        # Check if user exists
        influencers_collection = getNewInfluencerListFromMongoDB()
        user = influencers_collection.find_one(
            {'influencer_email': influencer_email})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Generate new password
        new_password = secrets.token_urlsafe(8)
        hashed_password = generate_password_hash(new_password)

        # Update password in database
        influencers_collection.update_one(
            {'influencer_email': influencer_email},
            {'$set': {
                'password': hashed_password
            }})

        return jsonify({'message': 'Password reset successfully'}), 200

    @app.route('/userdash')
    def get_userbroad():
        data = request.get_json()
        influencer_email = data.get('influencer_email')

        return jsonify({
            'message': 'Password reset successfully',
            'new_password': ""
        }), 200

    @app.route('/productlist')
    def get_user_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        influencers_collection = getNewInfluencerListFromMongoDB()
        influencer_data = influencers_collection.find_one(
            {'influencer_name': influencer_name})

        # If no document is found, return an error response
        if influencer_data is None:
            return jsonify({'message': 'Influencer not has products'}), 200

        products_list = influencer_data.get('product', [])

        return jsonify({
            'code': '0000',
            'data': {
                'products': products_list
            },
            'msg': 'success'
        })

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

    @app.route('/orderlist')
    def get_orderlist():
        data = request.get_json()
        orders_cursor = getOrderListFromMongoDB()
        influencer_name = data.get('influencer_name')
        products_cursor = getProductListFromMongoDB()
        orders_list = list(orders_cursor)

        return jsonify({
            'code': '0000',
            'data': {
                'orders': orders_list
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
