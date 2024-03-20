from pathlib import Path
import shopify
from flask import current_app, g
import os
import binascii
import json
import pandas as pd


class shoipfy_services:

    def __init__(self) -> None:

        # 连接shopify api
        shop_url = f"{current_app.config['SHOPIFY_SHOP_NAME']}.myshopify.com"
        api_version = '2024-01'
        private_app_password = current_app.config['SHOPIFY_API_PASSWORD']
        session = shopify.Session(shop_url, api_version, private_app_password)
        shopify.ShopifyResource.activate_session(session)

        self.script_dir = os.path.dirname(__file__)

    # 销毁时断开连接 del shoipfy_services
    def __del__(self):
        shopify.ShopifyResource.clear_session()

    def get_all_products(self):
        # 获取所有产品
        products = shopify.Product.find()
        return products

    def query_by_id(self,
                    shopifyApiId,
                    query_doc='pq.graphql',
                    operation_name='GetOneProduct'):

        query_document = Path(os.path.join(self.script_dir,
                                           query_doc)).read_text()

        response = shopify.GraphQL().execute(
            query=query_document,
            variables={"product_id": shopifyApiId},
            operation_name=operation_name)

        response = json.loads(response)

        # shopify.ShopifyResource.clear_session()
        return response


# connect with shopify api
def get_shopify_api():

    # 连接到shopify
    shop_url = f"{current_app.config['SHOPIFY_SHOP_NAME']}.myshopify.com"
    api_version = '2024-01'
    private_app_password = current_app.config['SHOPIFY_API_PASSWORD']
    session = shopify.Session(shop_url, api_version, private_app_password)
    shopify.ShopifyResource.activate_session(session)

    # shopify 寻找所有的product
    products = shopify.Product.find()

    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    document = Path(os.path.join(script_dir, "pq.graphql")).read_text()

    collection = g.db['test2']['products']

    for product in products:
        productId = f"gid://shopify/Product/{product.id}"

        productInfo = shopify.GraphQL().execute(
            query=document,
            variables={"product_id": productId},
            operation_name="GetOneProduct")
        productInfo = json.loads(productInfo)
        # print(productInfo)

        insert_value = {}

        insert_value['product'] = productInfo['data']['node']
        print(insert_value)
        # 将数据写入 MongoDB
        collection.insert_one(insert_value)
        # description 向量

    shopify.ShopifyResource.clear_session()


def extract_excel(path, collection_name):

    # 读取 Excel 文件
    df = pd.read_excel(path)
    # 选择数据库和集合
    collection = g.db['test2'][collection_name]

    if collection_name == "orders":
        data = df.apply(lambda row: convert_row_to_dict(row), axis=1).tolist()
    elif collection_name == "customers":
        data = df.apply(lambda row: convert_row_to_dict2(row), axis=1).tolist()

    # 将数据写入 MongoDB
    collection.insert_many(data)


# for orders excel
def convert_row_to_dict(row):
    order = {
        "name": row["Name"],
        "customer_email": row["Email"],
        "financial_status": row["Financial Status"],
        "paid_at": row["Paid at"],
        "fulfillment_status": row["Fulfillment Status"],
        "fulfilled_at": row["Fulfilled at"],
        "accepts_email_marketing": row["Accepts Marketing"],
        "currency": row["Currency"],
        "subtotal": row["Subtotal"],
        "Shipping": row["Shipping"],
        "Taxes": row["Taxes"],
        "Total": row["Total"],
        "promo_code": row["Discount Code"],
        "discount_amount": row["Discount Amount"],
        "shipping_method": row["Shipping Method"],
        "notes": row["Notes"],
        "note_attributes": row["Note Attributes"],
        "cancelled_at": row["Cancelled at"],
        "refunded_amount": row["Refunded Amount"],
        "vendor": row["Vendor"],
        "device_id": row["Device ID"],
        "id": row["Id"],
        "tags": row["Tags"],
        "risk_level": row["Risk Level"],
        "source": row["Source"],
        "phone": row["Phone"],
        "receipt_number": row["Receipt Number"],

    # 省略其它字段，直到 "lineitem"
        "lineitem": [{
            "created_at":
                row["Created at"],
            "lineitem_quantity":
                int(row["Lineitem quantity"]),
            "lineitem_name":
                row["Lineitem name"],
            "lineitem_price":
                float(row["Lineitem price"]),
            "lineitem_compare_at_price":
                float(row["Lineitem compare at price"]),
            "lineitem_sku":
                row["Lineitem sku"],
            "lineitem_requires_shipping":
                row["Lineitem requires shipping"],
            "lineitem_taxable":
                row["Lineitem taxable"],
            "lineitem_fulfillment_status":
                row["Lineitem fulfillment status"],
            "lineitem_discount":
                row["Lineitem discount"],
            "vendor":
                row["Vendor"],
    # 请为 lineitem 的其它字段添加转换逻辑
        }],
    # 省略其它字段，示意性代码
        "billing_info": {
            "name": row["Billing Name"],
            "street": row["Billing Street"],
            "address1": row["Billing Address1"],
            "address2": row["Billing Address2"],
            "company": row["Billing Company"],
            "city": row["Billing City"],
            "zip": row["Billing Zip"],
            "province": row["Billing Province"],
            "country": row["Billing Country"],
            "phone": row["Billing Phone"],
        },
        "shipping_info": {
            "name": row["Shipping Name"],
            "street": row["Shipping Street"],
            "address1": row["Shipping Address1"],
            "address2": row["Shipping Address2"],
            "company": row["Shipping Company"],
            "city": row["Shipping City"],
            "zip": row["Shipping Zip"],
            "province": row["Shipping Province"],
            "country": row["Shipping Country"],
            "phone": row["Shipping Phone"],
        },
        "tax": {
            "tax_1_name": row["Tax 1 Name"],
            "tax_1_value": row["Tax 1 Value"],
            "tax_2_name": row["Tax 2 Name"],
            "tax_2_value": row["Tax 2 Value"],
            "tax_3_name": row["Tax 3 Name"],
            "tax_3_value": row["Tax 3 Value"],
            "tax_4_name": row["Tax 4 Name"],
            "tax_4_value": row["Tax 4 Value"],
            "tax_5_name": row["Tax 5 Name"],
            "tax_5_value": row["Tax 5 Value"],
        },
        "payment": {
            "method": row["Payment Method"],
            "reference": row["Payment References"],
            "id": row["Payment ID"],
            "term": row["Payment Terms Name"],
            "next_payment_due_at": row["Next Payment Due At"],
        },
    }
    return order


# for customer excel
def convert_row_to_dict2(row):
    customer = {
        "customer_id": row["Customer ID"],
        "first_name": row["First Name"],
        "last_name": row["Last Name"],
        "customer_email": row["Email"],
        "accepts_email_marketing": row["Accepts Email Marketing"],
        "phone": row["Phone"],
        "accepts_sms_marketing": row["Accepts SMS Marketing"],
        "total_spent": row["Total Spent"],
        "total_orders": row["Total Orders"],
        "note": row["Note"],
        "tax_exempt": row["Tax Exempt"],
        "tags": row["Tags"],
        "default_address": {
            "address1": row["Default Address Address1"],
            "address2": row["Default Address Address2"],
            "company": None,
            "city": row["Default Address City"],
            "zip": row["Default Address Zip"],
            "province": row["Default Address Province Code"],
            "country": row["Default Address Country Code"],
            "phone": row["Default Address Phone"],
        },
    }

    return customer


if __name__ == '__main__':

    get_shopify_api()
