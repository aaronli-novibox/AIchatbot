import os
from flask import Flask, jsonify, request, url_for, render_template
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
from flaskr.db import get_mongo_db,close_db
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import json

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

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        influencer_email = data.get('influencer_email')
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

    # Login
    @app.route('/login', methods=['POST'])
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

        username = [promo['promo_code'].replace(encode, "") for promo in data if
                       promo['promo_code'].startswith(encode)]

        return jsonify({'message': 'Generate successful', 'promocode': encode}), 200

    @app.route('/promocode', methods=['POST'])
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

    # Forgot password endpoint
    @app.route('/forgot_password', methods=['POST'])
    def forgot_password():
        data = request.get_json()
        influencer_email = data.get('influencer_email')

        # Check if user exists
        # influencers_collection = getNewInfluencerListFromMongoDB()
        # user = influencers_collection.find_one({'influencer_email': influencer_email})
        # if not user:
        #     return jsonify({'error': 'User not found'}), 404
        
        token = s.dumps(influencer_email, salt='email-reset')
        msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[influencer_email])
        reset_path = '/session/reset-password/' + token
        ## Change to real Domain
        domain = app.config["BASEURL"]
        link = f"{domain}{reset_path}"
        #msg.body = f'Your link to reset your password is {link}'
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


    @app.route('/userdash')
    def get_userbroad():
        data = request.get_json()
        influencer_email = data.get('influencer_email')

        return jsonify({'message': 'Password reset successfully', 'new_password': ""}), 200

    @app.route('/productlist')
    def get_user_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        if not influencer_name :
            return jsonify({'message': 'Influencer name is required'}), 400
        products_list = getInflencerProductList(influencer_name)
        
        if not products_list:
            return jsonify({'message': 'Influencer not has products'}), 400
        
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