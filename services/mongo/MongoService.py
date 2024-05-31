from flask import g, current_app
import pandas as pd
import numpy as np
from flaskr.product_mongo import *
from mongoengine import Q


# return cursor type, and filter '_id' field
def getProductListFromMongoDB():

    products = Product.objects.only(
        'title',
        'shopify_id',
        'description',
        'featuredImage',
        'onlineStoreUrl',
        'priceRangeV2',
        'tags',
        'productType',
    ).exclude('id')

    return [product.to_mongo().to_dict() for product in products]    # 返回产品列表


def getOrderListFromMongoDB():

    orders = Order.objects.only('name',).exclude('id')

    return list(orders)    # 返回订单列表


def getCustomerListFromMongoDB():

    customers = Customer.objects.only('name', 'email').exclude('id')

    return [cus.to_mongo().to_dict() for cus in customers]    # 返回客户列表


def getInfluencerListFromMongoDB():

    influencers = Influencer.objects.only('influencer_name',
                                          'promo_code').exclude(
                                              'id', 'password', 'orders',
                                              'product')

    return [infl.to_mongo().to_dict() for infl in influencers]    # 返回影响者列表


def search_influencerList(search='', status=''):
    query = Q()

    if search:
        regex_pattern = f".*{search}.*"
        # 使用 Q 对象来构建 OR 查询，并进行不区分大小写的模糊搜索
        search_query = Q(influencer_name__iregex=regex_pattern) | Q(promo_code__iregex=regex_pattern)
        query &= search_query

    if status:
        status_query = Q(role=status)
        query &= status_query

    # 没有搜索词则返回所有影响者，并排除特定字段
    influencers = Influencer.objects(query).exclude('id', 'password', 'orders', 'product')
    influencer_list = [influ.to_mongo().to_dict() for influ in influencers]

    return influencer_list

def get_promocode(influencer_name=''):

    influencer = Influencer.objects(
        influencer_name=influencer_name).only('promo_code').first()
    if influencer:
        return influencer.promo_code
    return None


def replace_nan_with_none(data):
    """ Recursively replace NaN or None with None in any data structure. """
    if isinstance(data, list):
        return [replace_nan_with_none(item) for item in data]
    elif isinstance(data, dict):
        return {key: replace_nan_with_none(value) for key, value in data.items()}
    elif isinstance(data,
                    float) and pd.isna(data):    # Check for NaN of double type
        return None
    elif str(data) == "nan" or pd.isna(
            data):    # Check for string "NaN" and NaN
        return None
        return data.apply(replace_nan_with_none)
    elif isinstance(data,
                    pd.Timestamp):    # Check if data is a Timestamp object
        return str(data)
    else:
        return data


def process_data(data):
    """ Process data which might be nested lists, dicts, or DataFrame directly. """
    if isinstance(data, pd.DataFrame):
        return data.applymap(replace_nan_with_none)
    elif isinstance(data, (dict, list)):
        return replace_nan_with_none(data)
    else:
        return replace_nan_with_none(data)


def get_all_order():
    """
    接受包含订单数据的DataFrame，前后填充空的promo_code，转换并提取fulfilled_at列的年和月，
    然后按promo_code、年和月分组，计算每个组的订单总金额。

    """
    order_collection = g.db['test2']["new_filled_orders"]

    data = list(order_collection.find({}, {'_id': 0}))
    if data:
        df = pd.DataFrame(data)

        # 修正和转换fulfilled_at列，提取年和月
        df['fulfilled_at'] = df[
            'fulfilled_at'].str[:-6]    # Assuming '-06' needs to be removed
        df['fulfilled_at'] = pd.to_datetime(df['fulfilled_at'], errors='coerce')
        df['fulfilled_at'].fillna(method='bfill', inplace=True)

        # data['fulfilled_at'].fillna(method='ffill', inplace=True)
        df['year'] = df['fulfilled_at'].dt.year
        df['month'] = df['fulfilled_at'].dt.month

        # promo_code填充
        df['promo_code'].fillna(method='bfill', inplace=True)
        df['promo_code'].fillna(method='ffill', inplace=True)

        df['device_id'].fillna(value=0, inplace=True)
        df['phone'].fillna(value=0, inplace=True)

        # Replace all remaining NaN values with None in Nested Structures
        try:
            processed_df = process_data(df)
            return processed_df
        except Exception as e:
            print(e)
    else:
        return []


def filter_orders_by_code(df, promo_code):
    if promo_code in df['promo_code'].values:
        filtered_df = df[df['promo_code'] == promo_code]
        return filtered_df
    else:
        raise ValueError("没有使用该promo_code的订单")


def get_order_total(data):
    # 分组并计算每个组的订单总金额
    grouped_total = data.groupby(['promo_code', 'year', 'month']).agg({
        'subtotal': 'sum'
    }).reset_index()
    return grouped_total


def getOrdersFromMongoDB(promocode='',
                         search_term='',
                         start_time='',
                         end_time=''):
    df = get_all_order()
    order_list = []
    # if promocode:
    #     order_list = filter_orders_by_code(df, promocode).copy()
    # else:
    order_list = df.copy()

    influencer_collection = g.db['test2']["new_influencers"]
    influencer_list = list(influencer_collection.find({}, {'_id': 0}))
    influencer_data = pd.json_normalize(influencer_list,
                                        'product',
                                        meta=['influencer_name', 'promo_code'],
                                        record_prefix='product_')

    # 展开嵌入式文件并转化为DataFrame
    datalist = order_list.to_dict(orient='records')
    order_data = pd.json_normalize(
        datalist,
        'lineitem',
        meta=['name', 'promo_code', 'fulfilled_at', 'subtotal'],
        record_prefix='lineitem_')

    # order重命名
    order_data = order_data.rename(
        columns={'lineitem_lineitem_sku': 'lineitem_sku'})

    # 填充promo_code，修正和转换fulfilled_at列，提取年和月
    order_data['fulfilled_at'] = order_data['fulfilled_at'].str[:-6]
    order_data['fulfilled_at'] = pd.to_datetime(order_data['fulfilled_at'],
                                                errors='coerce')
    order_data['year'] = order_data['fulfilled_at'].dt.year
    order_data['month'] = order_data['fulfilled_at'].dt.month
    order_data['promo_code'].fillna(method='bfill', inplace=True)
    order_data['promo_code'].fillna(method='ffill', inplace=True)

    # 分组并计算每个promo_code各产品的订单总金额
    grouped_product_subtotal = order_data.groupby(
        ['promo_code', 'year', 'month', 'lineitem_sku']).agg({
            'subtotal': 'sum'
        }).reset_index()

    # 提取influencer分红信息
    influencer_commission_rate = influencer_data[[
        'promo_code', 'product_product_sku', 'product_commission'
    ]].rename(columns={'product_product_sku': 'lineitem_sku'})

    # 转换commission数据类型
    influencer_commission_rate[
        'product_commission'] = influencer_commission_rate[
            'product_commission'].str[:-1]
    influencer_commission_rate[
        'product_commission'] = influencer_commission_rate[
            'product_commission'].astype(int)

    # 拼接influencer分红信息和订单信息
    influencer_order_commission = pd.merge(grouped_product_subtotal,
                                           influencer_commission_rate,
                                           on=['promo_code', 'lineitem_sku'])

    # 计算分红
    influencer_order_commission[
        'Total_commission'] = influencer_order_commission[
            'product_commission'] * influencer_order_commission['subtotal']

    return influencer_order_commission


def insertInfluencerData(influencer_data):
    promo_codes = [data['promo_code'] for data in influencer_data]

    influencer_collection = g.db['test2']["new_influencers"]
    influencer_collection.insert_many(influencer_data)

    for code in promo_codes:
        if influencer_collection.find_one({"promo_code": code}):
            print(f"Duplicate promo code found: {code}. Aborting operation.")
            return 0

    else:
        influencer_collection.insert_many(influencer_data)
        print("Data inserted successfully.")
        return 1

def get_all_influencer_products(search_term=''):
    # Retrieve all influencers
    all_influencers = Influencer.objects()
    all_products = []

    for influencer in all_influencers:
        signed_products = influencer.product

        for product in signed_products:
            if product.product:
                # Prepare the product dictionary
                product_info = {
                    'title': product.product.title,
                    'username': influencer.influencer_name,
                    'commission_rate': product.commission,
                    'product_id': product.product.shopify_id,
                    'start_time': product.product_contract_start.strftime("%Y-%m-%d") if product.product_contract_start else "N/A",
                    'end_time': product.product_contract_end.strftime("%Y-%m-%d") if product.product_contract_end else "N/A",
                    'status': True if product.product_contract_end > datetime.now() else False,
                    'featuredImage': product.product.featuredImage,
                    'onlineStoreUrl': product.product.onlineStoreUrl,
                    'video_exposure': product.video_exposure,
                }

                normalized_search_term = search_term.strip().lower()
                if not normalized_search_term or normalized_search_term in product_info['title'].lower():
                    all_products.append(product_info)

    return all_products

def getInflencerProducts(influencer_name, search_term=''):

    # Get Influencers Infor and products
    influencer_info = Influencer.objects(
        influencer_name=influencer_name).first()
    if influencer_info is None:
        print(f"No influncer found with name {influencer_name}")
        return

    signed_products = influencer_info.product

    in_signed_products = []

    for one_product in signed_products:
            # Prepare the product dictionary
            if one_product.product:
                product_info = {
                    'title':
                        one_product.product.title,
                    'commission_rate':
                        one_product.commission,    # Default to '8%' if not specified
                    'product_shopify_id':
                        one_product.product.shopify_id,
                    'start_time':
                        one_product.product_contract_start.strftime("%Y-%m-%d")
                        if one_product.product_contract_start else "N/A",
                    'end_time':
                        one_product.product_contract_end.strftime("%Y-%m-%d")
                        if one_product.product_contract_end else "N/A",
                    'status':
                        True
                        if one_product.product_contract_end > datetime.now() else False,
                    'featuredImage':
                        one_product.product.featuredImage,
                    'onlineStoreUrl':
                        one_product.product.onlineStoreUrl,
                }

                normalized_search_term = search_term.strip().lower()
                if not normalized_search_term or normalized_search_term in product_info[
                        'title'].lower():
                    in_signed_products.append(product_info)
    return in_signed_products


# 获取所有签约的products 给管理员
def get_signed_Products(search_term=''):
    # Get Influencers Infor and products
    influencers_collection = g.db['test2']["new_influencers"]
    # Prepare a list to hold all unique signed products from all influencers
    all_signed_products = []

    for influencer_info in influencers_collection.find({}):

        signed_products = influencer_info['product']

        for product in signed_products:
            # Prepare the product dictionary
            product_info = {
                'title': product.get('product_name'),
                'commission_rate': product.get(
                    'commission', '8%'),    # Default to '8%' if not specified
                'status': True,
                'product_sku': product.get('product_sku'),
                'start_time': product.get('product_contract_start'),
                'end_time': product.get('product_contract_end')
            }

            normalized_search_term = search_term.strip().lower()
            if not normalized_search_term or normalized_search_term in product_info[
                    'title'].lower():
                all_signed_products.append(product_info)

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
    #         result['earnings_per_product'] = float(result['commission_rate'].replace('%', ''))/100 * price
    #     else:
    #         result['earnings_per_product'] =  price * 0.08
    #     result['total_commission'] += result['earnings_per_product'] * quantity

    return all_signed_products


# 获取所有products（products 这个列表）
def get_all_products_mongodb(influencer_instance, search_term=''):

    # Get all products
    if search_term:

        regex_pattern = f".*{search_term}.*"
        # 使用 MongoEngine 进行模糊搜索并确保产品状态为 "active"
        products = Product.objects(
            Q(title__iregex=regex_pattern) &
            Q(status="ACTIVE")    # 添加产品状态为 "active" 的条件
        ).only(
            'title',
            'shopify_id',
            'description',
            'featuredImage',
            'onlineStoreUrl',
            'priceRangeV2',
            'tags',
            'productType',
        ).exclude('id')

    else:
        products = Product.objects(status="ACTIVE"    # 仅选取状态为 "active" 的产品
                                  ).only(
                                      'title',
                                      'shopify_id',
                                      'description',
                                      'featuredImage',
                                      'onlineStoreUrl',
                                      'priceRangeV2',
                                      'tags',
                                      'productType',
                                  ).exclude('id')

    product_list = []

    for product in products:

        prod = influencer_instance.find_product_by_shopifyid(product.shopify_id)
        product_dict = product.to_mongo().to_dict()
        if prod:
            product_dict['commission_rate'] = prod.commission
        else:
            product_dict['commission_rate'] = "8%"

        product_list.append(product_dict)

    return product_list
