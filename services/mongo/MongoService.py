from flask import g, current_app
from datetime import datetime


# return cursor type, and filter '_id' field
def getProductListFromMongoDB():
    product_collection = g.db['test2']["products"]
    documents = product_collection.find({}, {'_id': 0})

    return documents


def getOrderListFromMongoDB():
    order_collection = g.db['test2']["orders"]
    documents = order_collection.find({}, {'_id': 0})

    return documents


def getCustomerListFromMongoDB():
    customer_collection = g.db['test2']["customers"]
    documents = customer_collection.find({}, {'_id': 0})

    return documents


def getInfluencerListFromMongoDB():
    customer_collection = g.db['test2']["influencers"]
    documents = customer_collection.find({}, {'_id': 0})

    return documents


def getNewInfluencerListFromMongoDB():
    influencer_collection = g.db['test2']["new_influencers"]

    return influencer_collection


def getOrdersFromMongoDB():
    order_collection = g.db['test2']["new_filled_orders"]

    return order_collection


def countInfluencers():
    influencer_collection = getNewInfluencerListFromMongoDB()
    count = influencer_collection.count_documents({})
    return count


def insertInfluencerData(influencer_data):
    promo_codes = [data['promo_code'] for data in influencer_data]

    influencer_collection = g.db['test2']["influencers"]
    influencer_collection.insert_many(influencer_data)

    for code in promo_codes:
        if influencer_collection.find_one({"promo_code": code}):
            print(f"Duplicate promo code found: {code}. Aborting operation.")
            return 0

    else:
        influencer_collection.insert_many(influencer_data)
        print("Data inserted successfully.")
        return 1


def getInflencerProductList(influencer_name, search_term=''):
    # Get Influencers Infor and products
    influencers_collection = g.db['test2']["new_influencers"]
    influencer_info = influencers_collection.find_one({'influencer_name': influencer_name},
                                                      {'product': 1, 'promo_code': 1})
    if influencer_info is None:
        print(f"No influncer found with name {influencer_name}")
        return
    signed_products = influencer_info['product']
    # promo_code = influencer_info['promo_code']

    # Get all products
    products_collection = g.db['test2']["products"]
    if search_term:
        regex_pattern = f".*{search_term}.*"  # Create a regex pattern for fuzzy search
        products = products_collection.find({"title": {"$regex": regex_pattern, "$options": "i"}},
                                            {'title': 1, '_id': 0})
    else:
        products = products_collection.find({}, {'title': 1, '_id': 0})
    products = list(products)
    for product in products:
        # Initiate atrributes
        product['commission_rate'] = '8%'
        product['status'] = False
        product['product_sku'] = None
        product['start_time'] = None
        product['end_time'] = None
        # product['total_products_purchased'] = 0
        # product['earnings_per_product'] = 0
        # product['total_commission'] = 0

        # check if the product is signed with a commission rate
        is_signed = next((item for item in signed_products if item['product_name'] == product['title']), None)
        if is_signed is not None:
            product['status'] = True
            product['product_sku'] = is_signed['product_sku']
            product['commission_rate'] = is_signed['commission']
            product['start_time'] = is_signed['product_contract_start']
            product['end_time'] = is_signed['product_contract_end']

    # # Get orders with promo code
    # orders = g.db['test2']['new_filled_orders']
    # orders = orders.find({'promo_code': promo_code, 'financial_status': 'paid'}, {'lineitem': 1})
    # for order in orders:
    #     #find corresponding product
    #     product_name = order['lineitem'][0]['lineitem_name']
    #     result = next((item for item in products if item['title'] == product_name), None)
    #     price = order['lineitem'][0]['lineitem_price']
    #     quantity = order['lineitem'][0]['lineitem_quantity']

    #     #update attributes
    #     result['total_products_purchased'] += quantity

    #     create_time = order['lineitem'][0]['created_at']
    #     # 看是否在带货列表中且购买日期在签约日期间
    #     create_time  = datetime.strptime(create_time , '%Y-%m-%d %H:%M:%S %z').strftime('%Y-%m-%d')
    #     create_time = datetime.strptime(create_time , '%Y-%m-%d')

    #     if result['status'] and create_time > datetime.strptime(result['start_time'], '%m-%d-%Y') and create_time < datetime.strptime(result['end_time'], '%m-%d-%Y'):
    #         #很奇怪，price是从order里获取的。如果同一个商品的不同order的不同price那怎么办
    #         result['earnings_per_product'] = float(result['commission_rate'].replace('%', ''))/100 * price
    #     else: 
    #         result['earnings_per_product'] =  price * 0.08
    #     result['total_commission'] += result['earnings_per_product'] * quantity

    return products
