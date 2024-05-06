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
from datetime import datetime, timedelta
from functools import wraps
from bson import binary
from io import BytesIO
import jwt
import base64

from dotenv import load_dotenv
from flask import g, request, redirect, url_for, jsonify, render_template
from flaskr.shp import *
from flaskr.oai import *
from flaskr.db import get_mongo_db, close_db
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
    # configure for email send
    app.config['SECRET_KEY'] = 'SECRETKEY'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Set in your environment variables
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Set in your environment variables
    app.config['TESTING'] = False
    app.config['BASEURL'] = os.getenv('BASEURL')
    app.config['BDEMAIL'] = os.getenv('BDEMAIL')
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
        gc.collect()  # 强制执行垃圾收集
        print("garbage", gc.garbage)  # 打印无法回收的对象列表

        return response

    @app.route('/register', methods=['POST'])
    def register():
        data = request.form
        file = request.files.get('avatar')
        confirm = False
        email = data['email']

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
        if email != app.config['BDEMAIL']:
            if influencers_collection.find_one({'influencer_email': email}):
                return jsonify({'error': 'Email already in use'}), 409

            # send authentication email
            # token = s.dumps(email, salt='email-confirm')
            # confirm_url = f"{app.config['BASEURL']}/confirm/{token}"
            # msg = Message("Please Confirm Your Email", recipients=[email])
            # msg.body = f"Please confirm your email by clicking on the following link: {confirm_url}"
            # mail.send(msg)
        else:
            confirm = True
            msg = Message("New Inflencer Added", recipients=[email])
            msg.body = f"New influencer {data['firstName']} has registered with this email"
            mail.send(msg)

        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # Prepare user data
        user_data = {
            "influencer_name": data.get('username'),
            "influencer_email": data.get('email'),
            "promo_code": data.get('promoCode'),
            "avatar": binary_data,
            "contract_start": None,
            "contract_end": None,
            "product": [],
            "first_name": data.get('firstName'),
            "last_name": data.get('lastName'),
            "middle_name": data.get('middleName'),
            "password": hashed_password,
            "role": 'influencer',
            "age": data.get('age'),
            "country": data.get('country'),
            "city_state": data.get('cityState'),
            "phone": data.get('phone'),
            "bio": data.get('bio'),
            "collaboration": data.get('collaborations'),
            "audience": data.get('audience'),
            "niche": data.get('niches'),
            "interest": data.get('interests'),
            "is_email_confirmed": confirm
        }

        # Insert into MongoDB
        influencers_collection.insert_one(user_data)
        return jsonify({'message': 'Registration successful'}), 201

    @app.route('/confirm/<token>', methods=['GET'])
    def confirm_email(token):
        try:
            email = s.loads(token, salt='email-confirm', max_age=3600)  # Token expires after 1 hour
            influencers_collection = getNewInfluencerListFromMongoDB();
            user = influencers_collection.find_one({'email': email})
            if user and not user['confirmed']:
                influencers_collection.update_one({'email': email}, {'$set': {'is_email_confirmed': True}})
                return jsonify(message="Email confirmed successfully"), 200
            return jsonify(message="Email already confirmed or token expired"), 400
        except SignatureExpired:
            return jsonify(message="The confirmation link has expired."), 400

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

    def safe_json_loads(data_str):
        try:
            return json.loads(data_str) if data_str and isinstance(data_str, str) else data_str
        except json.JSONDecodeError:
            return None

    @app.route('/update_influencer', methods=['POST'])
    def update_userinfo():
        data = request.form
        email = data.get('email')
        file = request.files.get('avatar')

        if not email:
            return jsonify({'error': 'Missing email field'}), 400

        # Get the MongoDB collection
        influencers_collection = getNewInfluencerListFromMongoDB()

        # Fetch the existing influencer information
        influencer = influencers_collection.find_one({'influencer_email': email})
        if not influencer:
            return jsonify({'error': 'Influencer not found'}), 404

        # Handle file update
        if file:
            # Convert file to binary
            file_stream = BytesIO()
            file.save(file_stream)
            file_stream.seek(0)
            binary_data = binary.Binary(file_stream.read())
        else:
            binary_data = None

        # Prepare updated data, only for fields that are allowed to change
        updated_data = {
            "age": data.get('age', influencer.get('age')),
            "country": data.get('country', influencer.get('country')),
            "city_state": data.get('cityState', influencer.get('city_state')),
            "phone": data.get('phone', influencer.get('phone')),
            "bio": data.get('bio', influencer.get('bio')),
            "collaboration": data.get('collaborations', influencer.get('collaboration')),
            "audience": data.get('audience', influencer.get('audience')),
            "niche": data.get('niches', influencer.get('niche')),
            "interest": data.get('interests', influencer.get('interest')),
            "is_email_confirmed": data.get('is_email_confirmed', influencer.get('is_email_confirmed')),
        }

        # Update the avatar only if it's present
        if binary_data is not None:
            updated_data["avatar"] = binary_data

        # Perform the update using $set to only modify allowed fields
        update_result = influencers_collection.update_one(
            {'influencer_email': email},
            {'$set': updated_data}
        )

        # Check if the update was successful
        if update_result.matched_count == 0:
            return jsonify({'error': 'Update failed'}), 500

        return jsonify({'message': 'User information updated successfully'}), 200

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
            return jsonify({'error': 'Email or promocode not found'}), 404

        # # Check if the email is confirmed
        # if user['is_email_confirmed']== False:
        #     return jsonify({'error': 'Email not confirmed'}), 401

        # Check password
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid password'}), 401

        # JWT creation with expiration time
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        # Convert MongoDB documents to a JSON serializable format
        user_data = {}
        for key, value in user.items():
            if isinstance(value, ObjectId):
                user_data[key] = str(value)
            elif isinstance(value, bytes):
                # Convert bytes to Base64 string if needed
                user_data[key] = base64.b64encode(value).decode('utf-8')
            elif key in ['collaboration', 'audience', 'niche', 'interest']:
                # Parse JSON strings into JSON objects
                user_data[key] = safe_json_loads(value)
            else:
                user_data[key] = value
        # print(user_data)
        return jsonify({'message': 'Login successful', 'user': user_data, 'token': token}), 200

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
    @validate_json('firstname', 'lastname')
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

        full_promo_code = encode + str(new_number)

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

        order_list = getOrderCollection().find({'promo_code': promocode}, {'_id': 0})
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

    # Forgot password endpoint
    @app.route('/forgot_password', methods=['POST'])
    def forgot_password():
        data = request.get_json()
        influencer_email = data.get('influencer_email')

        # Check if user exists
        influencers_collection = getNewInfluencerListFromMongoDB()
        user = influencers_collection.find_one({'influencer_email': influencer_email})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        token = s.dumps(influencer_email, salt='email-reset')
        msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[influencer_email])
        reset_path = '/session/reset-password/' + token
        ## Change to real Domain
        domain = app.config["BASEURL"]
        link = f"{domain}{reset_path}"
        # msg.body = f'Your link to reset your password is {link}'
        msg.html = render_template('email/email_template.html', link=link, username="Test")
        try:
            mail.send(msg)
            return jsonify({'message': 'Email Sent'}), 200  # Email sent successfully
        except Exception as e:
            print(e)
            return 500  # Email sending failed

    @app.route('/reset/<token>', methods=['GET', 'POST'])
    def reset_with_token(token):
        try:
            email = s.loads(token, salt='email-reset', max_age=1800)  # Token is valid for 30 min
        except SignatureExpired:
            return jsonify({'message': 'Token Expired'}), 404

        if request.method == 'POST':
            data = request.get_json()
            password = data.get('password')
            hashed_password = generate_password_hash(password)
            influencers_collection = getNewInfluencerListFromMongoDB()
            influencers_collection.update_one({'influencer_email': email},
                                              {'$set': {'password': hashed_password}})
            return jsonify({'message': 'Password reset successfully'}), 200
        return jsonify({'message': 'Token Valid'}), 200

    @app.route('/productlist', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_all_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        search_term = data.get('search', '')
        if not influencer_name:
            return jsonify({'message': 'Influencer name is required'}), 400
        products_list = get_all_products_mongodb(search_term)

        return jsonify({'products': products_list}), 200

    @app.route('/yourproducts', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_influencer_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        search_term = data.get('search', '')

        if not influencer_name:
            return jsonify({'message': 'Influencer name is required'}), 400

        products_list = getInflencerProducts(influencer_name, search_term)

        return jsonify({'products': products_list}), 200

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
        }), 200

    @app.route('/orderlist', methods=['POST'])
    def get_orderlist():
        data = request.get_json()
        search_term = data.get('search', '')
        role = data.get('role')
        influencer_name = data.get('influencer_name')
        promocode = None
        if role != ['ADMIN']:
            promocode = get_promocode(influencer_name=influencer_name)

        try:
            orderslist = getOrdersFromMongoDB(promocode=promocode)
            datalist = orderslist.to_dict(orient='records')
            return jsonify({'orders': datalist}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/orders')
    def getOrdersInfoFromMongoDB():
        orders_cursor = getOrderListFromMongoDB();
        orders_list = list(orders_cursor)

        return jsonify({
            'code': '0000',
            'data': {
                'orders': orders_list
            },
            'msg': 'success'
        }), 200

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

    @app.route('/influencerlist', methods=['POST'])
    def get_influencerlist():
        data = request.get_json()
        search_term = data.get('search', '')
        role = data.get('role')

        influencers = search_influencerList(search=search_term)
        influencers_list = list(influencers)

        if role == ['ADMIN']:
            return jsonify({'influencers': influencers_list}), 200
        else:
            return jsonify({'msg': 'Not admin account'}), 200

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
