import os
from flask import Flask, abort, send_file, g, request, redirect, jsonify, render_template
from services.mongo import *
from services.aichatbot.AIchatBotService import *
from services.mongo.MongoService import *
from services.webhook.webhookService import *
from bson.objectid import ObjectId
from flasgger.utils import swag_from
from flaskr.schemas import *
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_cors import CORS
from functools import wraps
from bson import binary
from flasgger import Swagger
import io
import jwt
import base64

from flaskr.shp import *
from flaskr.oai import *
from flaskr.db import get_mongo_db, close_db
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from mongoengine import connect, Q
from flaskr.product_mongo.influencer_doc import *
from flaskr.product_mongo.mongo_doc import *
import re
import hmac
import hashlib
from urllib.parse import urlencode

def load_model() -> FlagModel:
    # Load the model
    emb_model = FlagModel(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'services/aichatbot/models/models--BAAI--bge-large-en-v1.5/snapshots/d4aa6901d3a41ba39fb536a557fa166f842b0e09'
        ),
        query_instruction_for_retrieval=
        "Generate a representation for this sentence for retrieving items:",
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

    # config(app)
    # configure for email send
    # fmt: off
    app.config['SECRET_KEY'] = 'SECRETKEY'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Set in your environment variables
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Set in your environment variables
    app.config['TESTING'] = False
    app.config['BASEURL'] = os.getenv('BASEURL')
    app.config['BDEMAIL'] = os.getenv('BDEMAIL')
    app.config['MODEL'] = load_model()                             # Load the model for aichatbot service
    app.config['SWAGGER'] = {
        'title': 'Novi Box API',
        'uiversion': 3,
        'openapi': '3.0.2',
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/apispec_1.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/swagger/'
    }

    mail = Mail(app)

    # Initialize Swagger
    swagger = Swagger(app)

    # Serializer for creating the token
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    connect('dev', alias='default', host=app.config['MONGO_URI'])

    # fmt: on

    # router
    @app.before_request
    def before_request():

        # Connect to the openai service
        get_openai_service()

    @app.after_request
    def after_request(response):

        close_openai_service()

        return response

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
                if request.method == 'POST':
                    json_data = request.get_json()
                    if not json_data:
                        abort(400, description="Invalid or missing JSON")
                    missing_required = [
                        arg for arg in required_args if arg not in json_data
                    ]
                    if missing_required:
                        abort(
                            400,
                            description=
                            f"Missing {', '.join(missing_required)} in JSON data"
                        )

                    if one_of:
                        if not any(key in json_data for key in one_of):
                            abort(
                                400,
                                description=
                                f"At least one of {', '.join(one_of)} is required"
                            )

                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def safe_json_loads(data_str):
        try:
            return json.loads(data_str) if data_str and isinstance(
                data_str, str) else data_str
        except json.JSONDecodeError:
            return None

    @app.route('/register', methods=['POST'])
    @swag_from(register_schema)
    def register():
        data = request.form
        file = request.files.get('avatar')
        confirm = False
        email = data['email']
        first_name = data.get('firstName')

        collaborations = json.loads(data.get('collaborations', '[]'))
        niches = json.loads(data.get('niches', '[]'))
        interests = json.loads(data.get('interests', '[]'))
        audiences = json.loads(data.get('audience', '[]'))

        collaboration = [Collaboration(**data) for data in collaborations]
        niche = [Niche(**data) for data in niches]
        interest = [Interest(**data) for data in interests]

        if file:
            file_data = file.read()
            binary_data = binary.Binary(file_data)

        else:
            binary_data = None

        # send authentication email
        if email != app.config['BDEMAIL']:
            # Check if user already exists
            user = Influencer.objects(influencer_email=email).first()
            if user:
                return jsonify({'error': 'Email already in use'}), 409

            token = s.dumps(email, salt='email-confirm')
            confirm_url = f"{app.config['BASEURL']}/session/confirm/{token}"
            msg = Message("Please Verify Your Email",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.html = render_template('email_verfication.html',
                                       link=confirm_url,
                                       username=first_name)
        else:
            confirm = True
            msg = None
            print(f"New user {first_name} has registered with this email")

        hashed_password = generate_password_hash(data['password'],
                                                 method='pbkdf2:sha256')

        # Prepare user data
        user_data = {
            "influencer_name": data.get('username'),
            "influencer_email": data.get('email'),
            "promo_code": data.get('promoCode'),
            "avatar": binary_data,
            "first_name": data.get('firstName'),
            "last_name": data.get('lastName'),
            "middle_name": data.get('middleName'),
            "password": hashed_password,
            "role": 'customer',
            "age": data.get('age'),
            "country": data.get('country'),
            "state": data.get('state'),
            "city": data.get('city'),
            "zipcode": data.get('zipcode'),
            "shipping_address": data.get('shippingAddress'),
            "phone": data.get('phone'),
            "bio": data.get('bio'),
            "collaboration": collaboration,
            "audience": audiences,
            "niche": niche,
            "interest": interest,
            "is_email_confirmed": confirm
        }

        try:
            # Send email message only if msg is not None
            if msg:
                mail.send(msg)
            else:
                return jsonify({'message': 'Registration successful'}), 200
        except Exception as e:
            print(e)
            return jsonify({'message': 'Email sending failed'
                           }), 500    # Email sending failed

        # Save user data to MongoDB
        Influencer(**user_data).save()

        return jsonify({'message': 'Registration successful'}), 201
    
    @app.route('/resend', methods=['POST'])
    def resend_verification_email():
        data = request.get_json()
        email = data.get('email')
        first_name = data.get('firstName')
        token = s.dumps(email, salt='email-confirm')
        confirm_url = f"{app.config['BASEURL']}/session/confirm/{token}"
        msg = Message("Please Verify Your Email",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[email])
        msg.html = render_template('email_verfication.html',
                                    link=confirm_url,
                                    username=first_name)
        try:
            mail.send(msg)
            return jsonify({'message': 'Reset Email successful'}), 200
        except Exception as e:
            print(e)
            return jsonify({'message': 'Email sending failed'
                           }), 500 

    @app.route('/get_profile_photo/<influencer_name>', methods=['GET'])
    def get_profile_photo(influencer_name):
        user = Influencer.objects(influencer_name=influencer_name).first()

        if user and user['avatar']:
            return send_file(
                io.BytesIO(user['avatar']),
                mimetype=
                'image/jpeg'    # This assumes the image is JPEG. Adjust accordingly.
            )
        else:
            return jsonify({'error': 'No photo found'}), 404
        
    @app.route('/generate_social_post_url', methods=['GET'])
    def generate_social_post_url():
        platform = request.args.get('platform')
        user_name = request.args.get('influencer_name')
        user = Influencer.objects(influencer_name=user_name).first()
        promo_code = user.promo_code

        if platform == 'facebook':
            post_url = 'https://www.facebook.com/stories/create'
            text_to_copy = f"Special offer just for you! Use promo code:【{promo_code}】for 10% off at thenovibox.com. Click to enjoy exclusive savings!"

        elif platform == 'tiktok':
            post_url = 'https://www.tiktok.com/creator-center/upload'
            text_to_copy = f"Hey TikTok! Save 10% with code【{promo_code}】Swipe up to shop at thenovibox.com!"

        elif platform == 'instagram':
            post_url = 'https://www.instagram.com'
            text_to_copy = f"Unlock 10% off at thenovibox.com with my code:【{promo_code}】. Dive into the savings! Tap to shop! "

        elif platform == 'twitter':
            post_url = 'https://twitter.com/intent/tweet?' + urlencode({
                'text': f'Grab this deal!  Use {promo_code} for 10% off your next purchase at thenovibox.com. Shop now! '
            })
            text_to_copy = f"Grab this deal!  Use【{promo_code}】for 10% off your next purchase at thenovibox.com. Shop now! "

        else:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        return jsonify({'url': post_url, 'text': text_to_copy})

    @app.route('/confirm/<token>', methods=['GET'])
    def confirm_email(token):
        try:
            email = s.loads(token, salt='email-confirm',
                            max_age=3600)    # Token expires after 1 hour
            user = Influencer.objects(influencer_email=email).first()
            if user and not user.is_email_confirmed:
                user.update(set__is_email_confirmed=True)
                return jsonify(message="Email confirmed successfully"), 200
            return jsonify(message="Email already confirmed"), 200
        except SignatureExpired:
            return jsonify(message="The confirmation link has expired."), 400

    @app.route('/update_influencer', methods=['POST'])
    def update_userinfo():
        data = request.json
        influencer_name = data.get('influencer_name')

        if not influencer_name:
            return jsonify({'error': 'Missing influencer_name field'}), 400

        influencer = Influencer.objects(influencer_name=influencer_name).first()

        if not influencer:
            return jsonify({'error': 'Influencer not found'}), 404

        # Prepare updated data, only for fields that are allowed to change
        updated_data = {
            "set__age":
                data.get('age', influencer.get('age')),
            "set__first_name":
                data.get('first_name', influencer.get('first_name')),
            "set__middle_name":
                data.get('middle_name', influencer.get('middle_name')),
            "set__last_name":
                data.get('last_name', influencer.get('last_name')),
            "set__country":
                data.get('country', influencer.get('country')),
            "set__city_state":
                data.get('cityState', influencer.get('city_state')),
            "set__zipcode":
                data.get('zipcode', influencer.get('zipcode')),
            "set__phone":
                data.get('phone', influencer.get('phone')),
            "set__shipping_address":
                data.get('shippingAddress', influencer.get('shipping_address')),
            "set__bio":
                data.get('bio', influencer.get('bio')),
            "set__niche":
                data.get('niches', influencer.get('niche')),
            "set__interest":
                data.get('interests', influencer.get('interest')),
        }

        update_result = Influencer.objects(influencer_name=influencer_name).update_one(
            **updated_data)

        # 检查是否有文档被更新
        if update_result == 0:
            return jsonify({'error': 'Update failed'}), 500

        return jsonify({'message': 'User information updated successfully'
                       }), 200

    # Login
    @app.route('/login', methods=['POST'])
    @swag_from(login_schema)
    @validate_json('password', one_of=['email', 'promocode'])
    def login():
        data = request.get_json()
        influencer_identifier = data.get('email') or data.get('promocode')
        password = data.get('password')
        
        if influencer_identifier == app.config['BDEMAIL']:
            return jsonify({'error': 'Please use Promo Code to log'}), 415

        user = Influencer.objects(
            Q(influencer_email=influencer_identifier) |
            Q(promo_code=influencer_identifier)).exclude('id', 'orders', 'product').first()

        if not user:
            return jsonify({'error': 'Email or promocode not found'}), 404

        if not user.is_email_confirmed:
            return jsonify({'error': 'Email not confirmed'}), 400

        # check password
        if not check_password_hash(user.password, password):
            return jsonify({'error': 'Invalid password'}), 401

        # JWT creation with expiration time
        token = jwt.encode(
            {
                'user_id': str(user.id),
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            app.config['SECRET_KEY'],
            algorithm='HS256')

        # Convert MongoDB documents to a JSON serializable format
        user_data = serialize_object(user.to_mongo().to_dict())

        # Delete password
        if 'password' in user_data:
            del user_data['password']

        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'token': token
        }), 200
    
    def serialize_object(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        if isinstance(obj, dict):
            return {key: serialize_object(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [serialize_object(item) for item in obj]
        if isinstance(obj, Image):
            return {
                'url': obj.url
            }
        return obj

    @app.route('/checkusername', methods=['POST'])
    @swag_from(check_username_schema)
    @validate_json('username')
    def already_has_username():
        data = request.get_json()
        username = data.get('username')

        user = Influencer.objects(influencer_name=username).first()
        if user:
            return jsonify({'isUnique': False}), 200

        return jsonify({'isUnique': True}), 200

    @app.route('/checkemail', methods=['POST'])
    @swag_from(check_email_schema)
    @validate_json('email')
    def check_email():
        data = request.get_json()
        email = data.get('email')
        user = Influencer.objects(influencer_email=email).first()
        if user and email != app.config['BDEMAIL']:
            return jsonify({'isUnique': False}), 200
        return jsonify({'isUnique': True}), 200

    @app.route('/promocode', methods=['POST'])
    @swag_from(promo_generator_schema)
    @validate_json('firstname', 'lastname')
    def promo_generator():
        data = request.get_json()
        first = data.get('firstname')
        last = data.get('lastname')
        encode = (last[0].upper() + first[0].upper()).strip() + '_NOVIBOX_'

        regex = re.compile(f'^{re.escape(encode)}')
        existing_promos = Influencer.objects(promo_code=regex)

        # 提取 promo codes 中的数字部分
        promo_numbers = [
            int(promo.promo_code.replace(encode, ''))
            for promo in existing_promos
        ]

        if promo_numbers:
            new_number = max(promo_numbers) + 1
        else:
            new_number = 1

        full_promo_code = encode + str(new_number)

        return jsonify({
            'message': 'Generate successful',
            'promocode': full_promo_code
        }), 200

    @app.route('/checkpromocode', methods=['POST'])
    @swag_from(check_promo_schema)
    @validate_json('promocode')
    def check_promo():
        data = request.get_json()
        promocode = data.get('promocode')

        user = Influencer.objects(promo_code=promocode).first()
        if user:
            return jsonify({'isUnique': False}), 200

        return jsonify({'isUnique': True}), 200

    # TODO: need to confirm the details
    @app.route('/admindash', methods=['POST'])
    @validate_json('influencer_name', 'role')
    def get_adminbroad():
        data = request.get_json()
        influencer_name = data.get('influencer_name')

        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400

        role = data.get('role')
        if role != 'admin':
            return jsonify({'message': 'Permission Denied'}), 500
        
        all_influencers = Influencer.objects(role__ne='admin').count()

        last_month_sales = 0
        last_month_orders = 0

        products_list = getProductListFromMongoDB()

        influencer_data = Influencer.objects(
            influencer_name=influencer_name).first()

        if influencer_data is not None:
            # products_list = influencer_data.get('product', [])
            # TODO: get the necessary data from the influencer document
            product_details = []
            for influencer_product in influencer_data.product:
                product = influencer_product.product
                if product:
                    # 此时product是一个Product对象的引用，可以直接访问其字段
                    product_info = {
                        'title':
                            product.title,
                        "commission_rate":
                            influencer_product.commission,
                        'status':
                            True if product.product_contract_end
                            > datetime.now() else False,
                        "start_time":
                            influencer_product.product_contract_start.strftime(
                                "%Y-%m-%d")
                            if influencer_product.product_contract_start else
                            "N/A",
                        "end_time":
                            influencer_product.product_contract_end.strftime(
                                "%Y-%m-%d") if
                            influencer_product.product_contract_end else "N/A",
                        "video_exposure":
                            influencer_product.video_exposure,
                        'product_shopify_id':
                            product.product.shopify_id,
                        'featuredImage':
                            product.featuredImage,
                        'onlineStoreUrl':
                            product.onlineStoreUrl,
                    }
                    product_details.append(product_info)

        return jsonify({
            'data': {
                'all_influencers': all_influencers,
                'last_month_sales': last_month_sales,
                'last_month_orders': last_month_orders,
                'products': product_details
            }
        }), 200

    @app.route('/userdash', methods=['POST'])
    @swag_from(get_userbroad_schema)
    def get_userbroad():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        if influencer_name is None:
            return jsonify({'message': 'Influencer name is required'}), 400
        
        # Check if user exist
        influencer_data = Influencer.objects.get(
            influencer_name=influencer_name)
        if influencer_data is None:
            return jsonify({'error': 'Influencer not found'}), 404

        # role = data.get('role')    # 这是用来干什么的？
        range = data.get('range')
        month = data.get('month')
        
        # Total earnings in User dashboard
        total_earnings = influencer_data.total_commission
        monthly_stats = influencer_data.get_last_month_sold_products(month)
        last_month_orders = monthly_stats['total_quantity']
        last_month_earning = monthly_stats['total_revenue']
        
        top_products = []
        for time in range:
            result = influencer_data.get_top_ten_selling_products(time)
            top_products.append({time : result})
        
        return jsonify({
            'cards': {
                'total_earnings': total_earnings,
                'last_month_earning': last_month_earning,
                'last_month_sold_products': last_month_orders
            },
            'top_products': top_products
        }), 200


    # Forgot password endpoint
    @app.route('/forgot_password', methods=['POST'])
    @swag_from(forgot_password_schema)
    @validate_json('email')
    def forgot_password():
        data = request.get_json()
        influencer_email = data.get('email')

        # Check if user exists
        user = Influencer.objects(influencer_email=influencer_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if influencer_email == app.config['BDEMAIL']:
            return jsonify({'error': 'Please contact the administrator to change the password!'}), 415

        token = s.dumps(influencer_email, salt='email-reset')
        msg = Message('Password Reset Request',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[influencer_email])
        reset_path = '/session/reset-password/' + token
        # Change to real Domain
        domain = app.config["BASEURL"]
        link = f"{domain}{reset_path}"
        # msg.body = f'Your link to reset your password is {link}'
        msg.html = render_template('email_template.html',
                                   link=link,
                                   username=user.first_name)
        try:
            mail.send(msg)
            return jsonify({'message': 'Email Sent'
                           }), 200    # Email sent successfully
        except Exception as e:
            print(e)
            return jsonify({'message': 'Email sending failed'
                           }), 500    # Email sending failed

    @app.route('/reset/<token>', methods=['GET', 'POST'])
    @swag_from(reset_with_token_schema)
    @validate_json('password')
    def reset_with_token(token):
        try:
            email = s.loads(token, salt='email-reset',
                            max_age=1800)    # Token is valid for 30 min
        except SignatureExpired:
            return jsonify({'message': 'Token Expired'}), 400

        if request.method == 'POST':
            data = request.get_json()
            password = data.get('password')
            hashed_password = generate_password_hash(password)
            influencer = Influencer.objects(influencer_email=email).first()
            influencer.update(set__password=hashed_password)
            return jsonify({'message': 'Password reset successfully'}), 200

        return jsonify({'message': 'Token Valid'}), 200

    @app.route('/productlist', methods=['POST'])
    @swag_from(get_all_products_schema)
    @validate_json('influencer_name', 'role')
    def get_all_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        search_term = data.get('search', '')
        if not influencer_name:
            return jsonify({'message': 'Influencer name is required'}), 400

        influencer = Influencer.objects(influencer_name=influencer_name).first()
        if not influencer:
            return jsonify({'message': 'Influencer not found'}), 404

        products_list = get_all_products_mongodb(
            influencer,
            search_term,
        )

        return jsonify({'products': products_list}), 200

    @app.route('/yourproducts', methods=['POST'])
    @swag_from(get_influencer_products_schema)
    @validate_json('influencer_name', 'role')
    def get_influencer_products():
        data = request.get_json()
        influencer_name = data.get('influencer_name')
        search_term = data.get('search')

        if not influencer_name:
            return jsonify({'message': 'Influencer name is required'}), 400

        # Fetch the influencer by name
        influencer = Influencer.objects(influencer_name=influencer_name).first()

        if not influencer:
            return jsonify({'message': 'Influencer not found'}), 404

        # Filter products based on search_term if provided
        products_list = getInflencerProducts(influencer_name, search_term)
        serialized_products = [serialize_object(product) for product in products_list]

        return jsonify({'products': serialized_products}), 200

    # TODO: need to confirm the logic
    @app.route('/allproducts', methods=['POST'])
    @swag_from(get_bd_influencers_products_schema)
    @validate_json('influencer_name', 'role')
    def get_bd_influencers_products():
        data = request.get_json()
        role = data.get('role')
        search_term = data.get('search', '')  # 暂时改为不设置默认值，有问题指正我

        if not role:
            return jsonify({'message': 'Role name is required'}), 400

        # need to confirm the details
        products_list = get_all_influencer_products(search_term)
        serialized_products = [serialize_object(product) for product in products_list]

        return jsonify({'products': serialized_products}), 200

    @app.route('/orderlist', methods=['POST'])
    @swag_from(get_orderlist_schema)
    def get_orderlist():
        data = request.get_json()
        search_term = data.get('search')
        # role = data.get('role')
        influencer_name = data.get('influencer_name')

        influencer = Influencer.objects(influencer_name=influencer_name).first()
        if not influencer:
            return jsonify({'message': 'Influencer not found'}), 404

        return jsonify({'orders': influencer.get_orderlist(search_term)}), 200

    @app.route('/orders', methods=['POST'])

    def get_all_orderlist():
        data = request.get_json()
        search_term = data.get('search')
        role = data.get('role')

        if role == 'admin':
            return jsonify({'message': 'Influencer not found'}), 404

        return jsonify({'orders': ""}), 200


    @app.route('/influencers')
    def getInfluencersInfoFromMongoDB():

        influencers_list = getInfluencerListFromMongoDB()

        return jsonify({
            'data': {
                'influencers': influencers_list
            },
            'message': 'success'
        })

    @app.route('/influencerlist', methods=['POST'])
    @swag_from(get_influencerlist_schema)
    def get_influencerlist():
        data = request.get_json()
        search_term = data.get('search', '')
        role = data.get('role', '')
        status = data.get('status', '')

        if role == 'admin':
            influencers = search_influencerList(search=search_term, status=status)
            for influencer in influencers:
                if 'avatar' in influencer:
                    influencer['avatar'] = base64.b64encode(influencer['avatar']).decode('utf-8')

            return jsonify({'influencers': influencers}), 200
        else:
            return jsonify({'msg': 'Not admin account'}), 200

    @app.route('/influencer', methods=['POST'])
    @swag_from(get_influencer_info_schema)
    def get_influencer_info():
        data = request.get_json()
        influencer_name = data.get('influencer_name')

        user = Influencer.objects(influencer_name=influencer_name).exclude(
                'id', 'password', 'orders',
                'product').first()
        if not user:
            return jsonify({'message': 'Influencer not found'}), 404

        # Convert MongoDB documents to a JSON serializable format
        user_data = {}
        for key, value in user.to_mongo().items():
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
        return jsonify({'data': user_data}), 200

    #########################################################
    #################### aichatbot service ##################
    #########################################################
    @app.route('/user-typing', methods=['POST'])
    def user_typing():
        req = request.json
        try:
            res, status_code = userTyping(req)
            return jsonify(res), status_code
        except Exception as error:
            return jsonify({'message': error}), 400

    @app.route('/recommand-list', methods=['POST'])
    def recommand_by_list():
        req = request.json
        try:
            current_app.logger.info('recommand by list')
            res, status_code = recommandGiftByList(req)
            return jsonify(res), status_code
        except Exception as error:
            return jsonify({'message': error}), 400

    @app.route('/recommand-user-typing', methods=['POST'])
    def recommand_by_user_typing():
        data = request.get_json()
        user_input = data.get('user_typing')
        try:
            result = write_by_ai(user_input)
            return jsonify({'result': result}), 200
        except Exception as error:
            return jsonify({'error': error}), 400

    @app.route('/recommand-typing', methods=['POST'])
    def recommand_by_typing():
        data = request.get_json()
        try:
            res, status_code = recommandGiftByUserInput(data)
            return jsonify(res), status_code
        except Exception as error:
            return jsonify({
                'code': "0001",
                "data": None,
                'message': error
            }), 400

    @app.route('/gift-swip', methods=['POST'])
    def recommand_by_tags():
        data = request.get_json()
        try:
            res, status_code = recommandGiftByTags(data)
            return jsonify(res), status_code
        except Exception as error:
            return jsonify({'message': error}), 400

    #########################################################
    #####################  webhook service ##################
    #########################################################
    def verify_webhook(data, hmac_header):
        digest = hmac.new(app.config['SHOPIFY_API_PASSWORD'].encode('utf-8'),
                          data,
                          digestmod=hashlib.sha256).digest()
        computed_hmac = base64.b64encode(digest)

        return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

    @app.route('/webhook', methods=['POST'])
    def handle_webhook():

        data = request.get_data()
        # TODO: 现在不知道私钥是什么
        # verified = verify_webhook(data,
        #                           request.headers.get('X-Shopify-Hmac-SHA256'))

        # if not verified:
        #     abort(401)

        # Process webhook payload
        webhookService(data)

        return ('', 200)

    @app.route('/')
    def hello_novi_box():
        return "hello novi box"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
