from .basic_doc import *
from .mongo_doc import *
from mongoengine import Document, ValidationError, EmbeddedDocument, LazyReferenceField, EmbeddedDocumentField, ReferenceField, DoesNotExist, StringField, ListField, BinaryField, DecimalField
from datetime import datetime


class InfluencerProduct(EmbeddedDocument):

    product = ReferenceField(Product)
    commission = StringField(default="8%")
    # 好像不需要这个commission fee （from yamin）
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

    def get_orderlist(self):
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

                orderlist.append(product_order)

        return orderlist

    # 来一笔新订单，更新influencer的信息，webhook
    def append_order(self, order):

        order_info = OrderInfo(order=order).save()

        self.orders.append(order_info)

        # if order.displayFinancialStatus != "PAID":

        #     for li in order.lineitem:

        #         # 增加class中的order_nums (好像也不需要（from yamin)）
        #         self.order_nums += li.lineitem_quantity

        #         # 找到对应的product(签约的)
        #         product_details = self.find_product(li.product.id)

        #         if product_details and product_details.product_contract_start <= order.created_at and product_details.product_contract_end >= order.created_at:

        #             order_info.order_commission_fee += (
        #                 float(product_details.commission.replace('%', '')) /
        #                 100) * li.lineitem_quantity * li.lineitem_price

        #             # 增加class中的total_commission
        #             self.total_commission += order_info.order_commission_fee

        #             # 如果对应的commission_fee为0，那么就计算commission_fee？ 这里实在没看懂
        #             if product_details.commission_fee == 0:
        #                 product_details.commission_fee = (
        #                     float(product_details.commission.replace('%', '')) /
        #                     100) * li.lineitem_price

        #             product_details.save()

        #         else:
        #             order_info.order_commission_fee += 0.08 * li.lineitem_quantity * li.lineitem_price

        #             # 增加class中的total_commission
        #             self.total_commission += order_info.order_commission_fee

        #             # 如果对应的commission_fee为0，那么就计算commission_fee？ 这里实在没看懂
        #             if product_details.commission_fee == 0:
        #                 product_details.commission_fee = 0.08 * li.lineitem_price

        #             product_details.save()

        order_info.save()
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
