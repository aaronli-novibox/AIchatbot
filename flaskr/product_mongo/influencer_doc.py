from .basic_doc import *
from .mongo_doc import *
from mongoengine import Document, ValidationError, EmbeddedDocument, LazyReferenceField, EmbeddedDocumentField, ReferenceField, DoesNotExist, StringField, ListField, BinaryField, DecimalField
from datetime import datetime, timedelta

# fmt: off

class InfluencerProduct(EmbeddedDocument):

    product = ReferenceField(Product)
    commission = StringField(default="8%")
    commission_fee = DecimalField(default=0)
    product_contract_start = DateTimeField()
    product_contract_end = DateTimeField()
    video_exposure = StringField()

    def clean(self):
        if self.product_contract_end < self.product_contract_start:
            raise ValidationError("product_contract_end must be after product_contract_start")


class Platform(EmbeddedDocument):
    label = StringField()


class Collaboration(EmbeddedDocument):

    platform = EmbeddedDocumentField(Platform)
    link = StringField()


class Niche(EmbeddedDocument):
    label = StringField()
    group = StringField()


class Interest(EmbeddedDocument):
    label = StringField()
    group = StringField()


# class Audience(EmbeddedDocument):


class OrderInfo(EmbeddedDocument):
    order = ReferenceField(Order)
    order_commission_fee = DecimalField(default=0)


# novi box自建数据库，shopify没有的
class Influencer(Document):

    influencer_name = StringField(required=True)
    influencer_email = StringField()
    promo_code = StringField(
        required=True,
        unique=True,
    # TODO: default=generate_promo_code()，可以直接generate，不喜欢再改
    )    # 普通用户注册的需不需要promo code呢, default 先生成一个，不喜欢再改
    contract_start = DateTimeField(default=None)
    contract_end = DateTimeField(default=None)

    product = ListField(EmbeddedDocumentField(InfluencerProduct), default=[])

    first_name = StringField()
    middle_name = StringField()
    last_name = StringField()
    country = StringField()
    state = StringField()
    city = StringField()
    age = StringField()
    zipcode = StringField()
    audience = ListField(StringField(), default=[])
    phone = StringField()
    shipping_address = StringField()

    collaboration = ListField(EmbeddedDocumentField(Collaboration), default=[])
    niche = ListField(EmbeddedDocumentField(Niche), default=[])
    interest = ListField(EmbeddedDocumentField(Interest), default=[])
    password = StringField()

    type = StringField()
    bio = StringField()
    avatar = BinaryField()    # BINARY DATA
    role = StringField()

    orders = ListField(EmbeddedDocumentField(OrderInfo), default=[])

    order_nums = DecimalField(default=0)    # 订单中商品的数量
    total_commission = DecimalField(default=0)    # 总佣金

    is_email_confirmed = BooleanField()

    def get_orderlist(self, search_term = ''):
        all_orders = self.orders
        orderlist = []
        for order_info in all_orders:
            order = order_info.order  # Ensure OrderInfo has a reference to Order
            for li in order.lineitem:  # Ensure Order has a list of LineItem
                product_order = {}  # Order per product
                product_order['Name'] = li.lineitem_name
                product_order['ID'] = li.lineitem_sku
                product_order['Unit Price'] = li.lineitem_price
                product_order['Financial Status'] = order.displayFinancialStatus
                product_order['Paid at'] = order.processedAt
                product_order['Fulfilled at'] = order.closedAt
                product_order['Purchased'] = li.lineitem_quantity
                product_order['Total Price'] = li.lineitem_quantity * li.lineitem_price
                product_order['onlineStoreUrl'] = li.product.onlineStoreUrl
                product_order['featuredImage'] = li.product.featuredImage

                # Commission calculation
                product_details = self.find_product(li.product.id)
                if product_details and product_details.product_contract_start <= order.createdAt and product_details.product_contract_end >= order.createdAt:
                    product_order['Commission Rate'] = product_details.commission
                    try:
                        product_order['Commissions'] = float(product_details.commission.replace('%', '')) / 100 * li.lineitem_price * li.lineitem_quantity
                    except ValueError:
                        print("Cannot find the commission")
                        product_order['Commission Rate'] = '8%'
                        product_order['Commissions'] = 0.08 * li.lineitem_quantity * li.lineitem_price
                else:
                    product_order['Commission Rate'] = '8%'
                    product_order['Commissions'] = 0.08 * li.lineitem_quantity * li.lineitem_price

                normalized_search_term = search_term.strip().lower()
                if not normalized_search_term or normalized_search_term in product_order[
                        'Name'].lower():
                    orderlist.append(product_order)

        return orderlist

    # 来一笔新订单，更新influencer的信息，webhook
    def append_order(self, order):

        order_info = OrderInfo(order=order)

        self.orders.append(order_info)

        if order.displayFinancialStatus == "PAID":

            for li in order.lineitem:

                # 增加class中的order_nums
                self.order_nums += li.lineitem_quantity

                # 找到对应的product(签约的)
                product_details = self.find_product(li.product.id)

                if product_details and product_details.product_contract_start <= order.created_at and product_details.product_contract_end >= order.created_at:

                    li.commission_fee = (float(product_details.commission.replace('%', '')) /
                        100) * li.lineitem_quantity * li.lineitem_price

                    order_info.order_commission_fee += li.commission_fee

                    # 增加class中的total_commission
                    self.total_commission += li.commission_fee

                    product_details.save()

                else:
                    li.commission_fee = 0.08 * li.lineitem_quantity * li.lineitem_price

                    order_info.order_commission_fee += li.commission_fee
                    # 增加class中的total_commission
                    self.total_commission += li.commission_fee

                    product_details.save()

                li.save()


        self.save()

    def find_product(self, product_id):

        for ip in self.product:
            if ip.product and ip.product.id == product_id:
                return ip
        return None

    def find_product_by_shopifyid(self, product_id):

        for ip in self.product:
            if ip.product and ip.product.shopify_id == product_id:
                return ip
        return None

    def get_top_ten_selling_products(self, month):
        # Parse the month and get the start and end dates
        start_date = datetime.strptime(month, "%Y-%m")
        end_date = start_date + timedelta(days=31)  # This handles month end correctly

        # Aggregate the orders to get the total quantity sold and total price for each product within the specified month
        pipeline = [
            {
                '$match': {
                    '_id': self.id
                }
            },
            {
                '$unwind': '$orders'
            },
            {
                '$lookup': {
                    'from': 'order',
                    'localField': 'orders.order',
                    'foreignField': '_id',
                    'as': 'order_docs'
                }
            },
            {
                '$unwind': '$order_docs'
            },
            {
                '$match': {
                    'order_docs.createdAt': {
                        '$gte': start_date,
                        '$lt': end_date
                    }
                }
            },
            {
                '$unwind': '$order_docs.lineitem'
            },
            {
                '$group': {
                    '_id': '$order_docs.lineitem.product',
                    'total_quantity': {
                        '$sum': '$order_docs.lineitem.lineitem_quantity'
                    },
                    'revenue': {
                        '$sum': '$order_docs.lineitem.commission_fee'
                    }
                }
            },
            {
                '$sort': {
                    'total_quantity': -1
                }
            },
            {
                '$limit': 10
            },
            {
                '$lookup': {
                    'from': 'product',
                    'localField': '_id',
                    'foreignField': '_id',
                    'as': 'product_docs'
                }
            },
            {
                '$unwind': '$product_docs'
            },
            {
                '$project': {
                    'product_id': '$_id',
                    'total_quantity': 1,
                    'revenue': 1,
                    'product': '$product_docs'
                }
            }
        ]

        results = list(Influencer.objects.aggregate(pipeline))
        top_ten_products = []
        for product_info in results:
            one_product = {}

            one_product['revenue'] = product_info['revenue']
            one_product['unitsSold'] = product_info['total_quantity']

            product = product_info['product']
            one_product['product_name'] = product['title']
            one_product['imgUrl'] = product['featuredImage'].url if product['featuredImage'] else None
            one_product['onlineStoreUrl'] = product['onlineStoreUrl']
            
            product_details = self.find_product(product_info['product_id'])
            if product_details and product_details.product_contract_start <= start_date and product_details.product_contract_end >= end_date:
                one_product['commission'] = product_details.commission
            else:
                one_product['commission'] = '8%'

            top_ten_products.append(one_product)

        return top_ten_products

    def get_last_month_sold_products(self, month):
        # Parse the month and get the start and end dates
        start_date = datetime.strptime(month, "%Y-%m")
        end_date = start_date + timedelta(days=31)  # This handles month end correctly

        # Aggregate the orders to get the total quantity sold and total price for each product within the specified month
        pipeline = [
            {
                '$match': {
                    '_id': self.id
                }
            },
            {
                '$unwind': '$orders'
            },
            {
                '$lookup': {
                    'from': 'order',
                    'localField': 'orders.order',
                    'foreignField': '_id',
                    'as': 'order_docs'
                }
            },
            {
                '$unwind': '$order_docs'
            },
            {
                '$match': {
                    'order_docs.createdAt': {
                        '$gte': start_date,
                        '$lt': end_date
                    }
                }
            },
            {
                '$unwind': '$order_docs.lineitem'
            },
            {
                '$group': {
                    '_id': None,
                    'total_quantity': {
                        '$sum': '$order_docs.lineitem.lineitem_quantity'
                    },
                    'total_revenue': {
                        '$sum': '$order_docs.lineitem.commission_fee'
                    }
                }
            }
        ]

        results = list(Influencer.objects.aggregate(pipeline))
        if results:
            return results[0]
        else:
            return {'total_quantity': 0, 'total_revenue': 0}



# example
# influencer = Influencer(
#     influencer_name="Buse Keskin",
#     influencer_email="healthykitchenohio@gmail.com",
#     promo_code="BUSEK10",
#     contract_start=datetime.strptime("02-18-2024", "%m-%d-%Y"),
#     contract_end=datetime.strptime("02-18-2025", "%m-%d-%Y"),
#     role="influencer",
# )

# # 保存一个influencer
# product = Product.objects(title="需要一个定位商品的字段").first()    # 需要一个定位商品的字段

# if product is None:
#     # 创建一个influencer的逻辑
#     # 其中，order的逻辑应该是：来一个新的order，webhook中进行解决，再说
#     influncer_product = InfluencerProduct(
#         product=product,
#         commission="15%",
#         product_contract_start=datetime.strptime("02-18-2024", "%m-%d-%Y"),
#         product_contract_end=datetime.strptime("02-18-2025", "%m-%d-%Y"))
#     influencer.product.append(influncer_product)
#     influencer.save()
# else:
#     print("Product not found.")

# # 从mongo中获取influencer，数据

# influencer = Influencer.objects(promo_code="BUSEK10").first()
# if influencer:
#     print(influencer.influencer_name)
#     print(influencer.product[0].product.title)
#     print(influencer.product[0].commission)

#     print(influencer.product[0].product.shopify_id)
#     print(influencer.product[0].product.description)
#     print(influencer.product[0].product.productType)
#     print(influencer.product[0].product.vendor)
#     print(influencer.product[0].product.status)
#     print(influencer.product[0].product.tags)
#     print(influencer.product[0].product.featuredImage)    # 图片链接
#     print(influencer.product[0].product.onlineStoreUrl)    # shopify网站链接
#     print(influencer.product[0].product.priceRangeV2)    # 价格范围
#     print(influencer.product[0].product.createdAt)
#     print(influencer.product[0].product.updatedAt)

#     for variant in influencer.product[0].product.variants:
#         print(variant.title)
#         print(variant.price)
#         print(variant.sku)    # 子商品sku
#         print(variant.createdAt)
#         print(variant.displayName)
#         print(variant.image)

#     print(influencer.orders[0].customer.name)
#     print(influencer.orders[0].fullyPaid)
#     # ...

# else:
#     print("Influencer not found.")
