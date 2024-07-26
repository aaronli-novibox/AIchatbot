from .basic_doc import *
from .mongo_doc import *
from mongoengine import Document, ValidationError, EmbeddedDocument, LazyReferenceField, EmbeddedDocumentField, ReferenceField, DoesNotExist, StringField, ListField, BinaryField, DecimalField, FloatField
from datetime import datetime, timedelta
import calendar
from .table import *
from django.db.models import Prefetch
from mongoengine import Q

# fmt: off

class InfluencerProduct(EmbeddedDocument):

    product = ReferenceField(Product)
    commission = StringField(default="8%")
    commission_fee = FloatField(default=0)
    product_contract_start = DateTimeField()
    product_contract_end = DateTimeField()
    video_exposure = StringField()
    review_status = StringField()
    pre_commission = StringField()

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
    )
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

    order_nums = IntField(default=0)  # 总计的订单数量
    product_nums = DecimalField(default=0)    # 订单中商品的数量
    total_commission = FloatField(default=0)    # 总佣金
    promo_code_used = IntField(default=0)    # 使用的promo code数量 => 即订单中不同商品的数量

    is_email_confirmed = BooleanField()

    def get_orderlist(self, search_term=''):
        all_orders = self.orders
        orderlist = []

        for order_info in all_orders:
            order = order_info.order  # Ensure OrderInfo has a reference to Order
            for li in order.lineitem:  # Ensure Order has a list of LineItem
                product_order = {}  # Order per product
                product_order['name'] = li.lineitem_name
                product_order['id'] = li.lineitem_sku
                product_order['unit_price'] = float(li.lineitem_price)
                product_order['status'] = order.displayFinancialStatus.value if order.displayFinancialStatus else None  # Convert to string
                product_order['paid_at'] = order.createdAt.strftime("%Y-%m-%d") if order.createdAt else 'N/A'
                product_order['fulfilled_at'] = order.closedAt.strftime("%Y-%m-%d") if order.closedAt else 'N/A'
                product_order['purchased'] = li.lineitem_quantity
                product_order['total_price'] = float(li.lineitem_quantity * li.lineitem_price)
                product_order['commission_rate'] = li.commission
                product_order['commissions'] = li.commission_fee

                # Fetch the Product document lazily
                product = li.product.fetch() if li.product else None
                if product:
                    product_order['onlineStoreUrl'] = product.onlineStoreUrl if product.onlineStoreUrl else ''
                    product_order['featuredImage'] = product.featuredImage.url if product.featuredImage else None

                    # Normalize and filter search term
                    normalized_search_term = search_term.strip().lower()
                    if not normalized_search_term or normalized_search_term in product_order['name'].lower():
                        orderlist.append(product_order)
                # else:
                #     print(product_order['Name'])
        return orderlist

    # 来一笔新订单，更新influencer的信息，webhook
    def append_order(self, order):
        '''
        只有order status是paid才能append到self.orders。
        只有从paid变成refund，并且在self.orders里，直接update self.orders，并且减去数据。
        '''

        # Check if the order is already in self.orders
        found = False
        for i, existing_order in enumerate(self.orders):
            if existing_order.order.shopify_id == order.shopify_id:
                # Replace the existing order with the new order
                self.orders[i].order = order
                found = True

        if not found and (order.displayFinancialStatus.value == "PAID" or order.displayFinancialStatus.value == "PARTIALLY_REFUNDED") :
            order_info = OrderInfo(order=order)
            self.orders.append(order_info)
            self.order_nums +=1

            for li in order.lineitem:
                order.quantity += li.lineitem_quantity

            for li in order.lineitem:

                # 增加class中的order_nums
                self.product_nums += li.lineitem_quantity
                # order.quantity += li.lineitem_quantity
                self.promo_code_used += 1

                # 找到对应的product
                product = li.product.fetch() if li.product else None
                if product:
                    # 更新product的amount
                    product.amount += li.lineitem_quantity
                    product.revenue += li.lineitem_quantity * li.lineitem_price

                    # 以下是签约的产品
                    product_details = self.find_product(product.id)
                    if product_details and product_details.product_contract_start <= order.createdAt and product_details.product_contract_end >= order.createdAt:

                        li.commission = product_details.commission
                        li.commission_fee =(float(product_details.commission.replace('%', '')) /
                            100) * li.lineitem_quantity * li.lineitem_price

                        order_info.order_commission_fee += li.commission_fee
                        order.order_commission_fee += li.commission_fee

                        product_details.commission_fee += li.commission_fee

                        # 增加class中的total_commission
                        self.total_commission += li.commission_fee

                        # 找成本的实例
                        product_pricing = Product_Pricing.objects(Product_List__sku=li.lineitem_sku).first()
                        if product_pricing and product_pricing.Cost:

                            li.profit = li.lineitem_quantity * li.lineitem_price - product_pricing.Cost.Vendor_price / product_pricing.Exchange_Rate - li.commission_fee - product_pricing.Cost.Self_shipping_cost * li.lineitem_quantity / order.quantity
                            order.order_profit += li.profit

                        else:
                            # 没有找到商品成本
                            li.profit = li.lineitem_quantity * li.lineitem_price - li.commission_fee
                            order.order_profit += li.profit


                    else:
                        li.commission = '8%'
                        li.commission_fee = 0.08 * li.lineitem_quantity * li.lineitem_price

                        order_info.order_commission_fee += li.commission_fee
                        order.order_commission_fee += li.commission_fee

                        # 增加class中的total_commission
                        self.total_commission += li.commission_fee

                        # 找成本的实例
                        product_pricing = Product_Pricing.objects(Product_List__sku=li.lineitem_sku).first()
                        if product_pricing and product_pricing.Cost:

                            li.profit = li.lineitem_quantity * li.lineitem_price - product_pricing.Cost.Vendor_price / product_pricing.Exchange_Rate - li.commission_fee - product_pricing.Cost.Self_shipping_cost * li.lineitem_quantity / order.quantity
                            order.order_profit += li.profit

                        else:
                            # 没有找到商品成本
                            li.profit = li.lineitem_quantity * li.lineitem_price - li.commission_fee
                            order.order_profit += li.profit

                    li.save()
                    order.save(validate=False)

        if found and order.displayFinancialStatus.value == "REFUND":
            for li in order.lineitem:
                self.order_nums -=1
                # 减去class中的order_nums
                self.product_nums -= li.lineitem_quantity

                self.promo_code_used -= 1

                order.quantity -= li.lineitem_quantity
                order.order_commission_fee -= li.commission_fee

                order_info.order_commission_fee -= li.commission_fee

                self.total_commission -= li.commission_fee

                # 找到对应的product
                product = li.product.fetch() if li.product else None
                if product:
                    product.amount -= li.lineitem_quantity
                    product.revenue -= li.lineitem_quantity * li.lineitem_price
                    product_details = self.find_product(product.id)
                    if product_details:
                        product_details.commission_fee -= li.commission_fee

                    # 找成本的实例
                    # product_pricing = Product_Pricing.objects(Product_List__sku=li.lineitem_sku).first()
                    # if product_pricing:
                    # 这里有些问题，部分退款等问题
                    order.order_profit = 0

                li.commission_fee == 0
                li.save()
                order.save(validate=False)

        self.save()

    def fake_data(self, order):
        if order.displayFinancialStatus.value == "PAID":
            for li in order.lineitem:

                # 增加class中的order_nums
                if self.product_nums == 0:
                    self.product_nums += li.lineitem_quantity
                #order.quantity += li.lineitem_quantity

                # 找到对应的product
                product = li.product.fetch() if li.product else None
                if product:
                    # 更新product的amount
                    print('Product Found:', product.title)
                    if product.amount == 0:
                        product.amount += li.lineitem_quantity
                    if product.revenue == 0:
                        product.revenue += li.lineitem_quantity * li.lineitem_price

                    # 以下是签约的产品
                    product_details = self.find_product(product.id)
                    print('commission: ', order.order_commission_fee)
                    if product_details and product_details.product_contract_start <= order.createdAt and product_details.product_contract_end >= order.createdAt:
                        print('signed product')
                        if li.commission == 0:
                            print()
                            li.commission = product_details.commission
                            li.commission_fee =(float(product_details.commission.replace('%', '')) /
                                100) * li.lineitem_quantity * li.lineitem_price

                            order.order_commission_fee += li.commission_fee

                            product_details.commission_fee += li.commission_fee

                            # 增加class中的total_commission
                            self.total_commission += li.commission_fee

                    else:
                        if li.commission == 0:
                            li.commission = '8%'
                            li.commission_fee = 0.08 * li.lineitem_quantity * li.lineitem_price
                            order.order_commission_fee += li.commission_fee

                            # 增加class中的total_commission
                            self.total_commission += li.commission_fee

                    li.save()
                    order.save(validate=False)

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
        start_date, end_date = get_start_and_end_dates(month)

        product_sales = {}

        for order_info in self.orders:
            order = order_info.order
            # Filter orders by the specified month
            if start_date <= order.createdAt < end_date and (order.displayFinancialStatus.value == "PAID" or order.displayFinancialStatus.value == "PARTIALLY_REFUNDED"):
                for line_item in order.lineitem:
                    if line_item.product:
                        product = line_item.product.fetch()
                        product_id = str(product.id)
                        if product_id in product_sales:
                            product_sales[product_id]['quantity'] += line_item.lineitem_quantity
                            product_sales[product_id]['revenue'] += line_item.commission_fee
                        else:
                            product_sales[product_id] = {
                                'product': product,
                                'quantity': line_item.lineitem_quantity,
                                'revenue': line_item.commission_fee,
                            }

        # Sort the products by quantity sold in descending order and get the top 10
        top_ten_products = sorted(product_sales.values(), key=lambda x: x['quantity'], reverse=True)[:10]

        result = []
        for item in top_ten_products:
            product = item['product']
            quantity = item['quantity']
            revenue = item['revenue']

            product_data = {
                'product_name': product.title,
                'unitsSold': quantity,
                'revenue': revenue,  # Ensure revenue is float
                'imgUrl': product.featuredImage.url if product.featuredImage else None,
                'onlineStoreUrl': product.onlineStoreUrl,
            }

            product_details = self.find_product(product.id)
            if product_details and product_details.product_contract_start <= start_date and product_details.product_contract_end >= end_date:
                product_data['commission'] = product_details.commission
            else:
                product_data['commission'] = '8%'

            result.append(product_data)
        return result

    def get_last_month_sold_products(self, month):
        start_date, end_date = get_start_and_end_dates(month)

        total_quantity = 0
        total_revenue = 0.0

        for order_info in self.orders:
            order = order_info.order
            # Filter orders by the specified month
            if start_date <= order.createdAt < end_date and (order.displayFinancialStatus.value == "PAID" or order.displayFinancialStatus.value == "PARTIALLY_REFUNDED"):
                for line_item in order.lineitem:
                    if line_item.product:  # Ensure product is not None
                        total_quantity += line_item.lineitem_quantity
                        total_revenue += line_item.commission_fee

        return {
            'total_quantity': total_quantity,
            'total_revenue': total_revenue  # Convert Decimal to float for JSON serialization
        }

    def get_last_month_sales(self, month):
        if self.role != 'admin':
            return False

        start_date, end_date = get_start_and_end_dates(month)
        all_orders = Order.objects()
        total_sales = 0
        for order in all_orders:
            if start_date <= order.createdAt < end_date and (order.displayFinancialStatus.value == "PAID" or order.displayFinancialStatus.value == "PARTIALLY_REFUNDED"):
                try:
                    total_sales += order.totalPriceSet.shopMoney.amount
                except:
                    print(order.id)
        return total_sales

def get_start_and_end_dates(month):
    # Parse the start date
    start_date = datetime.strptime(month, "%Y-%m")

    # Get the last day of the month
    last_day = calendar.monthrange(start_date.year, start_date.month)[1]

    # Create the end date
    end_date = start_date.replace(day=last_day) + timedelta(days=1)

    return start_date, end_date


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
