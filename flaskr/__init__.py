import os
from flask import Flask, abort
from services.mongo import *
from services.aichatbot.AIchatBotService import *
from services.mongo.MongoService import *
from bson.objectid import ObjectId
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_cors import CORS
from datetime import datetime
from functools import wraps
from bson import binary
from io import BytesIO

from dotenv import load_dotenv
from flask import g, request, redirect, url_for, jsonify
from flaskr.shp import *
from flaskr.oai import *
from flaskr.db import get_mongo_db,close_db
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# from config import config

# from .openai import get_openai_client


def config(app):

    load_dotenv()
    app.config["SHOPIFY_API_KEY"] = os.getenv("SHOPIFY_API_KEY")
    app.config["SHOPIFY_API_PASSWORD"] = os.getenv("SHOPIFY_API_PASSWORD")
    app.config["SHOPIFY_SHOP_NAME"] = os.getenv("SHOPIFY_SHOP_NAME")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["OPENAI_KEY"] = os.getenv("OPENAI_KEY")
    app.config["BASEURL"] = os.getenv("BASEURL")


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

    #config(app)
    #configure for email send
    app.config['SECRET_KEY'] = 'SECRETKEY'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Set in your environment variables
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Set in your environment variables
    app.config['TESTING'] = False
    mail = Mail(app)

    # Serializer for creating the token
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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
        data = request.form
        file = request.files['avatar']
        file = request.files.get('avatar')

        if file:
            # Convert file to binary
            file_stream = BytesIO()
            file.save(file_stream)
            file_stream.seek(0)
            binary_data = binary.Binary(file_stream.read())
        else:
            binary_data = None
        influencers_collection = getNewInfluencerListFromMongoDB();
        # Check if user already exists
        if influencers_collection.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already in use'}), 409

        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # Prepare user data
        user_data = {
            'firstName': data.get('firstName'),
            'lastName': data.get('lastName'),
            'email': data.get('email'),
            'password': hashed_password,
            'avatar': binary_data,
            'country': data.get('country'),
            'cityState': data.get('cityState'),
            'phone': data.get('phone'),
            'bio': data.get('bio'),
            'promoCode': data.get('promoCode'),
            'collaborations': data.get('collaborations'),
            'audience': data.get('audience'),
            'niches': data.get('niches'),
            'shippingAddress': data.get('shippingAddress'),
            'role': 'influencer'
        }

        # Insert into MongoDB
        influencers_collection.insert_one(user_data)
        return jsonify({'message': 'Registration successful'}), 201

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

    @app.route('/checkusername', methods=['POST'])
    @validate_json('username')
    def already_has_username():
        data = request.get_json()
        username = data.get('username')
        isUnique = True
        influencers_collection = getNewInfluencerListFromMongoDB();
        # Find user by username
        user = influencers_collection.find_one({'influencer_name': username})
        if user:
            isUnique = False
        return jsonify({'isUnique': isUnique}), 200

    @app.route('/checkemail', methods=['POST'])
    @validate_json('email')
    def check_email():
        data = request.get_json()
        email = data.get('email')
        isUnique = True
        influencers_collection = getNewInfluencerListFromMongoDB();
        # Find user by email
        email = influencers_collection.find_one({'influencer_email': email})
        if email:
            isUnique = False
        return jsonify({'isUnique': isUnique}), 200

    @app.route('/promocode', methods=['POST'])
    def promo_generator():
        data = request.get_json()
        first = data.get('firstname')
        last = data.get('lastname')
        encode = (last[0].upper() + first[0].upper()).strip() + '_NOVIBOX_'

        influencers_collection = getNewInfluencerListFromMongoDB();
        regex = f'^{encode}'
        existing_promos = list(influencers_collection.find({'promo_code': {'$regex': regex}}))
        promo_numbers = [int(promo['promo_code'].replace(encode, '')) for promo in existing_promos]

        if promo_numbers:
            new_number = max(promo_numbers) + 1
        else:
            new_number = 1

        return jsonify({'message': 'Generate successful', 'promocode': encode}), 200

        return jsonify({'message': 'Generate successful', 'promocode': full_promo_code}), 200

    @app.route('/checkpromocode', methods=['POST'])
    @validate_json('promocode')
    def check_promo():
        data = request.get_json()
        promocode = data.get('promocode')
        isUnique = True
        influencers_collection = getNewInfluencerListFromMongoDB();
        # Find user by promocode
        user = influencers_collection.find_one({'promo_code': promocode})
        if user:
            isUnique = False

        return jsonify({'isUnique': isUnique}), 200

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
            'data': {
                'all_influencers': all_influencers,
                'last_month_sales': last_month_sales,
                'last_month_orders': last_month_orders,
                'products': products_list
            }
        }), 200

    @app.route('/userdash', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_userbroad():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        role = data.get('role')
        search = data.get('search')
        products_list = []
        influencer_name = data.get('influencer_name')
        influencers_collection = getNewInfluencerListFromMongoDB();
        user = influencers_collection.find_one({'influencer_name': influencer_name})
        promocode = user['promo_code']
        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        influencers_collection = getNewInfluencerListFromMongoDB()
        influencer_data = influencers_collection.find_one({'influencer_name': influencer_name})

        if influencer_data is not None:
            products_list = influencer_data.get('product', [])

        order_nums = 0
        Total_Commissions = 0
        last_month_orders = 0

        order_list = getOrdersFromMongoDB().find({'promo_code': promocode}, {'_id': 0})
        # 遍历所有相关订单
        for doc in order_list:
            if doc['financial_status'] == "refunded":
                pass
            # 订单创建时间
            create_time = doc['lineitem'][0]['created_at']
            # 解析时间戳字符串,并只选取年月日
            create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S %z').strftime('%Y-%m-%d')
            create_time = datetime.strptime(create_time, '%Y-%m-%d')
            for product in products_list:
                if not product['commission_fee']:
                    product['commission_fee'] = 0
                # 看是否在带货列表中且购买日期在签约日期间
                if product['product_sku'] == doc['lineitem'][0]['lineitem_sku'] and create_time > datetime.strptime(
                        product['product_contract_start'], '%m-%d-%Y') and create_time > datetime.strptime(
                    product['product_contract_end'], '%m-%d-%Y'):
                    # 如果单个商品的分红值还是0， 就更新，不然就pass
                    if product['commission_fee'] == 0:
                        product['commission_fee'] = product['commission'] * doc['lineitem'][0]['lineitem_price']
                    else:
                        pass
                    # 增加带货数
                    order_nums += doc['lineitem'][0]['lineitem_quantity']
                    # 增加总分红数
                    Total_Commissions += doc['lineitem'][0]['lineitem_quantity'] * product['commission'] * \
                                         doc['lineitem'][0]['lineitem_price']

        return jsonify({
            'cards': {
                'all_orders': order_nums,
                'last_month_sales': Total_Commissions,
                'last_month_orders': last_month_orders
            },
            'products': products_list
        }), 200

    # # Forgot password endpoint
    # @app.route('/forgot_password', methods=['POST'])
    # def forgot_password():
    #     data = request.get_json()
    #     influencer_email = data.get('influencer_email')
    #
    #     # Check if user exists
    #     # influencers_collection = getNewInfluencerListFromMongoDB()
    #     # user = influencers_collection.find_one({'influencer_email': influencer_email})
    #     # if not user:
    #     #     return jsonify({'error': 'User not found'}), 404
    #
    #     token = s.dumps(influencer_email, salt='email-reset')
    #     msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[influencer_email])
    #     reset_path = '/session/reset-password/' + token
    #     ## Change to real Domain
    #     domain = app.config["BASEURL"]
    #     link = f"{domain}{reset_path}"
    #     #msg.body = f'Your link to reset your password is {link}'
    #     msg.html = render_template('email/email_template.html', link=link, username="Test")
    #     try:
    #         mail.send(msg)
    #         return jsonify({'message': 'Email Sent'}), 200  # Email sent successfully
    #     except Exception as e:
    #         print(e)
    #         return 500  # Email sending failed
    #
    # @app.route('/reset/<token>', methods=['GET', 'POST'])
    # def reset_with_token(token):
    #     try:
    #         email = s.loads(token, salt='email-reset', max_age=1800)  # Token is valid for 30 min
    #     except SignatureExpired:
    #         return jsonify({'message': 'Token Expired'}), 404
    #
    #     if request.method == 'POST':
    #         data = request.get_json()
    #         password = data.get('password')
    #         hashed_password = generate_password_hash(password)
    #         influencers_collection = getNewInfluencerListFromMongoDB()
    #         influencers_collection.update_one({'influencer_email': email},
    #                                           {'$set': {'password': hashed_password}})
    #         return jsonify({'message': 'Password reset successfully'}), 200
    #     return jsonify({'message': 'Token Valid'}), 200

    @app.route('/productlist', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_user_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        search_term = data.get('search', '')
        if not influencer_name:
            return jsonify({'message': 'Influencer name is required'}), 400
        products_list = getInflencerProductList(influencer_name, search_term)

        if not products_list:
            return jsonify({'message': 'Influencer not has products'}), 400

        print("product success")

        return jsonify({'products': products_list}), 200
        
        print("product success")

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
        search_term = data.get('search', '')
        orders_cursor = getOrderListFromMongoDB()
        influencer_name = data.get('influencer_name')
        influencers_collection = getNewInfluencerListFromMongoDB();
        user = influencers_collection.find_one(
            {'$or': [{'influencer_name': influencer_name}]})
        promocode = user['promo_code']
        role = data.get('role')
        orderslist = []

        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        if role == ['ADMIN']:
            orderslist = getOrderListFromMongoDB()
        else:
            orderslist = getOrdersFromMongoDB().find_one({'promo_code': promocode})
        # Convert ObjectId to string if present
        if orderslist and '_id' in orderslist:
            orderslist['_id'] = str(orderslist['_id'])

        return jsonify({'orders': orderslist}), 200

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