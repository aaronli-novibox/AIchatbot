import os
from flask import Flask, abort
from services.aichatbot.AIchatBotService import *
from services.mongo.MongoService import *
from bson.objectid import ObjectId
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_cors import CORS

from dotenv import load_dotenv
from functools import wraps
from flask import g, request, redirect, url_for, jsonify
from flaskr.shp import *
from flaskr.oai import *
from flaskr.db import get_mongo_db,close_db
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

    # config(app)

    # router
    @app.before_request
    def before_request():

        # connect to mongodb
        get_mongo_db()
        get_openai_service()

    @app.after_request
    def after_request(response):
        close_db()
        close_openai_service()
        import gc
        gc.collect()    # 强制执行垃圾收集
        print("garbage", gc.garbage)    # 打印无法回收的对象列表

        return response

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        influencer_email = data.get('influencer_email')
        # Add more required info
        password = data.get('password')

        # Check if influencer_name or influencer_email already exists
        influencers_collection = getNewInfluencerListFromMongoDB();
        existing_user = influencers_collection.find_one(
            {'$or': [{'influencer_name': influencer_name}, {'influencer_email': influencer_email}]})
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        # Save user to database
        # influencers_collection.insert_one({
        #     'influencer_name': influencer_name,
        #     'influencer_email': influencer_email,
        #     'password': hashed_password,
        #     'verification_token': verification_token
        # })

        return jsonify({'message': 'User registered successfully', 'role': 'editor'}), 201

    def role_required(*roles):
        def wrapper(fn):
            @wraps(fn)
            def decorated_view(*args, **kwargs):
                if g.user is None or g.user.role not in roles:
                    return jsonify({'error': 'Access denied'}), 403
                return fn(*args, **kwargs)

            return decorated_view

        return wrapper

    def validate_json(*required_args, one_of=None):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                json_data = request.get_json()
                if not json_data:
                    abort(400, description="Invalid or missing JSON")
                missing_required = [arg for arg in required_args if arg not in json_data]
                if missing_required:
                    abort(400, description=f"Missing {', '.join(missing_required)} in JSON data")

                if one_of:
                    if not any(key in json_data for key in one_of):
                        abort(400, description=f"At least one of {', '.join(one_of)} is required")

                return fn(*args, **kwargs)

            return wrapper

        return decorator

    # Login
    @app.route('/login', methods=['POST'])
    @validate_json('password', one_of=['email', 'promocode'])
    def login():
        data = request.get_json()
        influencer_identifier = data.get('email') or data.get('promocode')
        password = data.get('password')

        influencers_collection = getNewInfluencerListFromMongoDB();
        # Find user by influencer_name or influencer_email
        user = influencers_collection.find_one(
            {'$or': [{'promo_code': influencer_identifier}, {'influencer_email': influencer_identifier}]})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check password
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid password'}), 401

        # Convert MongoDB documents to a JSON serializable format
        user_data = {k: str(v) if isinstance(v, ObjectId) else v for k, v in user.items()}

        return jsonify({'message': 'Login successful', 'user': user_data}), 200

    @app.route('/username', methods=['POST'])
    @validate_json('firstname', 'lastname')
    def generate_username():
        data = request.get_json()
        first = data.get('firstname')
        last = data.get('lastname')
        encode = (last[0].upper() + first[0].upper()).strip()

        req = 'influencers'  # 'products' / 'customers
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
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")

        username = [name['influencer_name'].replace(encode, "") for name in data if
                       name['influencer_name'].startswith(encode)]

        return jsonify({'message': 'Generate successful', 'username': encode}), 200

    @app.route('/promocode', methods=['POST'])
    @validate_json('firstname', 'lastname')
    def promo_generator():
        data = request.get_json()
        first = data.get('firstname')
        last = data.get('lastname')
        encode = (last[0].upper() + first[0].upper()).strip() + '_NOVIBOX_'

        req = 'influencers'  # 'products' / 'customers
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
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")

        promo_codes = [promo['promo_code'].replace(encode, "") for promo in data if
                       promo['promo_code'].startswith(encode)]
        if promo_codes:
            encode = encode + str(sorted(list(map(int, promo_codes)))[-1] + 1)
        else:
            encode = encode + "1"

        return jsonify({'message': 'Generate successful', 'promocode': encode}), 200

    @app.route('/updatepromocode', methods=['POST'])
    @validate_json('promocode')
    def promo_change():
        data = request.get_json()
        encode = data.get('promocode')

        req = 'influencers'  # 'products' / 'customers
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
            print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        promo_codes = [promo['promo_code'].replace(encode, "") for promo in data if
                       promo['promo_code'].startswith(encode)]
        if promo_codes:
            encode = encode + str(sorted(list(map(int, promo_codes)))[-1] + 1)
        else:
            encode = encode + "1"

        return jsonify({'message': 'Update successful', 'promocode': encode}), 200

    @app.route('/admindash', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_adminbroad():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        role = data.get('role')
        products_list = []
        influencer_list = []
        all_influencers = countInfluencers()
        last_month_sales = 0
        last_month_orders = 0

        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        if role == ['ADMIN']:
            products_list = getProductListFromMongoDB()

        influencers_collection = getNewInfluencerListFromMongoDB()
        influencer_data = influencers_collection.find_one({'influencer_name': influencer_name})

        if influencer_data is not None:
            products_list = influencer_data.get('product', [])

        return jsonify({
            'code': '0000',
            'data': {
                'all_influencers': all_influencers,
                'last_month_sales': last_month_sales,
                'last_month_orders': last_month_orders,
                'products': products_list
            },
            'msg': 'success'
        }), 200

    @app.route('/userdash', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_userbroad():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        role = data.get('role')
        products_list = []
        orders = 12
        last_month_sales = 12
        last_month_orders = 30

        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        influencers_collection = getNewInfluencerListFromMongoDB()
        influencer_data = influencers_collection.find_one({'influencer_name': influencer_name})

        if influencer_data is not None:
            products_list = influencer_data.get('product', [])

        return jsonify({
            'cards': {
                'all_orders': orders,
                'last_month_sales': last_month_sales,
                'last_month_orders': last_month_orders
            },
            'products': products_list
        }), 200

    @app.route('/productlist', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_user_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        role = data.get('role')
        products_list = []

        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        if role == ['ADMIN']:
            products_list = getProductListFromMongoDB()
        else:
            influencers_collection = getNewInfluencerListFromMongoDB()
            influencer_data = influencers_collection.find_one({'influencer_name': influencer_name})

            if influencer_data is not None:
                products_list = influencer_data.get('product', [])

        return jsonify({ 'products': products_list }), 200

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

    @app.route('/orderlist', methods=['POST'])
    def get_orderlist():
        data = request.get_json()
        promo_code = data.get('promo_code')
        orders_list = []
        role = data.get('role')

        orders_collection = getOrderListFromMongoDB()

        if role == ['ADMIN']:
            orders_list = orders_collection.find({})
        else:
            orders_list = list(orders_collection.find({'promo_code': promo_code}))

        return jsonify({ 'orders': orders_list }), 200

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

    @app.route('/influencers', methods=['POST'])
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