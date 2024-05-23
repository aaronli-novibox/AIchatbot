# test data
from product_mongo import *
from mongoengine import connect
import os
from dotenv import load_dotenv

from datetime import datetime
import pytz
import pandas as pd

import re


def extract_number_from_string(s):
    """
    Extracts the number from a given string.

    Parameters:
    s (str): The input string containing a number.

    Returns:
    str: The extracted number as a string.
    """
    match = re.search(r'\d+', s)
    if match:
        return match.group(0)
    return None


def convert_edt_to_utc(edt_time_str):
    """
    Convert a given EDT/EST time string to UTC time.

    Parameters:
    edt_time_str (str): The EDT/EST time string in the format '%Y-%m-%d %H:%M:%S %z'.

    Returns:
    str: The UTC time string in the format '%Y-%m-%d %H:%M:%S'.
    """
    # Define the time format with timezone information
    time_format = '%Y-%m-%d %H:%M:%S %z'

    # Parse the input time string into a datetime object
    local_time = datetime.strptime(edt_time_str, time_format)

    # Convert the local time to UTC
    utc_time = local_time.astimezone(pytz.utc)

    # Return the UTC time as a string
    return utc_time.strftime('%Y-%m-%d %H:%M:%S')


load_dotenv()
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_PASSWORD = os.getenv("SHOPIFY_API_PASSWORD")
SHOPIFY_SHOP_NAME = os.getenv("SHOPIFY_SHOP_NAME")
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_KEY = os.getenv("OPENAI_KEY")
CLUSTER_ENDPOINT = os.getenv("CLUSTER_ENDPOINT")
TOKEN = os.getenv("TOKEN")
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")

connect('dev', alias='default', host=MONGO_URI)

promo_code = 'MZ_NOVIBOX_5'

influencer = Influencer.objects(promo_code=promo_code).first()
# influencer.orders = []
# influencer.save()
# import sys

# sys.exit()

# Read the Excel file
data = pd.read_excel(
    '/Users/tengyp/work/NoviBox/backend/AIchatbot/orders_export_test_data.xlsx')

last_order = None

# i = 0

# Iterate over the data
for index, row in data.iterrows():

    # Access individual values
    name = row['Name']

    name_num = extract_number_from_string(name)
    if int(name_num) > 99999:

        shopify_id = 'test_data' + name

        order = Order.objects(shopify_id=shopify_id).first()
        if not order:
            email = row['Email']
            displayFinancialStatus = row['Financial Status']
            createdAt = row['Paid at']
            print(name)
            print(createdAt)
            createdAt = convert_edt_to_utc(createdAt)

            displayFulfillmentStatus = row['Fulfillment Status']
            closedAt = row['Fulfilled at']

            if str(closedAt) != 'nan':
                print(closedAt)
                closedAt = convert_edt_to_utc((closedAt))

            currencyCode = row['Currency']
            subtotalLineItemsQuantity = row['Lineitem quantity']

            subtotal = row['Subtotal']
            subtotalPriceSet = MoneyBag(
                presentmentMoney=MoneyV2(amount=subtotal,
                                         currencyCode=currencyCode),
                shopMoney=MoneyV2(amount=subtotal, currencyCode=currencyCode))
            shipping = row['Shipping']
            totalShippingPriceSet = MoneyBag(
                presentmentMoney=MoneyV2(amount=shipping,
                                         currencyCode=currencyCode),
                shopMoney=MoneyV2(amount=shipping, currencyCode=currencyCode))

            taxes = row['Taxes']
            totalTaxSet = MoneyBag(presentmentMoney=MoneyV2(
                amount=taxes, currencyCode=currencyCode),
                                   shopMoney=MoneyV2(amount=taxes,
                                                     currencyCode=currencyCode))
            total = row['Total']
            totalPriceSet = MoneyBag(
                presentmentMoney=MoneyV2(amount=total,
                                         currencyCode=currencyCode),
                shopMoney=MoneyV2(amount=total, currencyCode=currencyCode))
            discount_amount = row['Discount Amount']
            totalDiscountsSet = MoneyBag(
                presentmentMoney=MoneyV2(amount=discount_amount,
                                         currencyCode=currencyCode),
                shopMoney=MoneyV2(amount=discount_amount,
                                  currencyCode=currencyCode))

            customerAcceptsMarketing = row['Accepts Marketing']
            order = Order(
                shopify_id=shopify_id,
                name=name,
                email=email,
                displayFinancialStatus=displayFinancialStatus.upper(),
                createdAt=createdAt,
                displayFulfillmentStatus=displayFulfillmentStatus.upper(),
                closedAt=closedAt,
                currencyCode=currencyCode,
                subtotalPriceSet=subtotalPriceSet,
                totalShippingPriceSet=totalShippingPriceSet,
                totalTaxSet=totalTaxSet,
                totalPriceSet=totalPriceSet,
                totalDiscountsSet=totalDiscountsSet,
                subtotalLineItemsQuantity=subtotalLineItemsQuantity,
                lineitem=[],
                customerAcceptsMarketing=customerAcceptsMarketing)
            order.save(validate=False)

        li = LineItem.objects(shopify_id='test_data_lineitem' + name +
                              row['Lineitem name']).first()

        if not li:
            li = LineItem(
                shopify_id='test_data_lineitem' + name + row['Lineitem name'],
                lineitem_name=row['Lineitem name'],
                lineitem_quantity=row['Lineitem quantity'],
                lineitem_price=row['Lineitem price'],
                lineitem_compare_at_price=row['Lineitem compare at price'],
                lineitem_sku=str(row['Lineitem sku']),
                lineitem_requires_shipping=row['Lineitem requires shipping'],
                lineitem_taxable=row['Lineitem taxable'],
                lineitem_fulfillment_status=row['Lineitem fulfillment status'],
                lineitem_discount=row['Lineitem discount'],
            # vendor=row['Vendor'] if row['Vendor'] else '',
                order=order,
                product=None,
                variant=None)

        title = str(row['Lineitem name'])
        product = Product.objects(title=title).first()
        product_variant = ProductVariant.objects(product=product).first()

        li.product = product
        li.variant = product_variant
        li.commission_fee = int(li.lineitem_price) * int(
            li.lineitem_quantity) * 0.08

        li.save()
        order.lineitem.append(li)
        order.save(validate=False)

        influencer.append_order(order)
        influencer_product = InfluencerProduct(
            product=product,
            product_contract_start=datetime.strptime("02-18-2024", "%m-%d-%Y"),
            product_contract_end=datetime.strptime("02-18-2025", "%m-%d-%Y"))
        if influencer_product not in influencer.product:
            influencer.product.append(influencer_product)

        influencer.save()
        # i += 1
        # if i == 6:
        #     break

    # 下面随便写的，必填项，但是现在没有用到/或者没有数据

    # billingAddressMatchesShippingAddress = True
    # canMarkAsPaid = True
    # canNotifyCustomer = True
    # capturable = True
    # confirmed = True

    # currentCartDiscountAmountSet = totalDiscountsSet
    # currentSubtotalLineItemsQuantity = subtotalLineItemsQuantity
    # currentSubtotalPriceSet = subtotalPriceSet

    # currentTotalDiscountsSet = totalDiscountsSet
    # currentTotalPriceSet = totalPriceSet
    # currentTotalTaxSet = None
    # currentTotalWeight = None
    # edited = False
    # estimatedTaxes = True
    # fulfillable = True
    # fullyPaid = True
    # hasTimelineComment = True
    # legacyResourceId = None
    # merchantEditable = True
    # netPaymentSet = None
    # originalTotalPriceSet = None
    # paymentCollectionDetails = None
    # processedAt = createdAt
    # refundDiscrepancySet = None
    # refundable = True
    # requiresShipping = True
    # restockable = True
    # returnStatus = None
    # taxesIncluded = True
    # taxExempt = None
    # test = True
