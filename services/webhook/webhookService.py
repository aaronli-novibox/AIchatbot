from pathlib import Path
from flask import current_app, g
import shopify
import json
from flaskr.product_mongo import *
import numpy as np


def webhookService(headers, json_data):

    topic = headers.get('X-Shopify-Topic')
    current_app.logger.info(topic)
    current_app.logger.info(json_data)

    if topic in ['orders/create', 'orders/updated']:

        data_item = shopify.Order.find(json_data.get("id", None))

        document = Path('flaskr/query_files/orders.graphql').read_text()
        dataInfo = shopify.GraphQL().execute(query=document,
                                             variables={"order_id": dataId},
                                             operation_name="GetOneOrder")

        dataInfo = json.loads(dataInfo)
        item = flatten_data(dataInfo)

        # 获取customer之前的订单，所使用的influncer的promo_code
        customer = Customer.objects(shopify_id=item['customer']['id']).first()

        promo_code = item['discountCode']

        if not promo_code:

            customer = Customer.objects(
                shopify_id=item['customer']['id']).first()
            promo_code = customer.lastOrder.discountCode

        item = recursive_replace_keys(item, key_changes)

        order, _ = Order.recursive_get_or_create(item)

        lineitems = []
        for li in data_item.line_items:

            product_instance = Product.objects(
                shopify_id=f"gid://shopify/Product/{li.product_id}").first()
            variant_instance = ProductVariant.objects(
                shopify_id=f"gid://shopify/ProductVariant/{li.variant_id}"
            ).first()

            lineitem_instance = LineItem.objects(
                shopify_id=li.admin_graphql_api_id).first()

            if lineitem_instance:
                lineitem_instance.lineitem_quantity = li.quantity
                lineitem_instance.lineitem_name = li.name
                lineitem_instance.lineitem_price = li.price
                lineitem_instance.lineitem_sku = li.sku
                lineitem_instance.lineitem_requires_shipping = li.requires_shipping
                lineitem_instance.lineitem_taxable = li.taxable
                lineitem_instance.lineitem_fulfillment_status = li.fulfillment_status
                lineitem_instance.lineitem_discount = li.total_discount
                lineitem_instance.vendor = li.vendor
                lineitem_instance.order = order
                lineitem_instance.product = product_instance
                lineitem_instance.variant = variant_instance
                lineitem_instance.save()
                lineitems.append(lineitem_instance)

            else:

                lineitems.append(
                    LineItem(shopify_id=li.admin_graphql_api_id,
                             lineitem_quantity=li.quantity,
                             lineitem_name=li.name,
                             lineitem_price=li.price,
                             lineitem_sku=li.sku,
                             lineitem_requires_shipping=li.requires_shipping,
                             lineitem_taxable=li.taxable,
                             lineitem_fulfillment_status=li.fulfillment_status,
                             lineitem_discount=li.total_discount,
                             vendor=li.vendor,
                             order=order,
                             product=product_instance,
                             variant=variant_instance).save())

        order.lineitem = lineitems
        order.save()

        # 加上influencer的逻辑
        influencer = Influencer.objects(promo_code=promo_code).first()

        if influencer:
            if order not in influencer.orders:
                influencer.append_order(order)
                influencer.save()
            else:
                # 更新订单
                pass

        return order

    elif topic in ['products/create', 'products/update']:

        data_item = shopify.Product.find(json_data.get("id", None))

        emb_model = current_app.config['EMB_MODEL']

        dataId = json_data.get("id", None)

        document = Path(f'flaskr/query_files/product.graphql').read_text()

        dataInfo = shopify.GraphQL().execute(query=document,
                                             variables={"product_id": dataId},
                                             operation_name="GetOneProduct")

        dataInfo = json.loads(dataInfo)
        # pprint(dataInfo)
        item = flatten_data(dataInfo)
        item = recursive_replace_keys(item, key_changes)

        product, _ = Product.recursive_get_or_create(item)

        description = item["description"]
        title = item["title"]
        vector_title = f'title: {title}, description: {description}'

        description_vector = emb_model.encode(vector_title).astype(np.float64)

        product.descriptionVector = description_vector.tolist()

        product.handle = data_item.handle

        metafields = data_item.metafields()

        for metafield in metafields:
            # print(metafield.key)
            # print(metafield.value)

            metafields_instance = Metafield.objects(
                shopify_id=f'gid://shopify/Metafield/{metafield.id}').first()

            if isinstance(metafield.value,
                          str) and 'MediaImage' in metafield.value:

                document = Path(
                    'flaskr/query_files/mediaImage.graphql').read_text()
                dataInfo = shopify.GraphQL().execute(
                    query=document,
                    variables={"media_image_id": metafield.value},
                    operation_name="GetOneMediaImage")
                dataInfo = json.loads(dataInfo)
                # pprint(dataInfo)
                item = flatten_data(dataInfo)
                value = item['image']['url']

            else:
                value = metafield.value

            if metafields_instance:
                metafields_instance.key = f'{metafield.key}'
                metafields_instance.value = f'{value}'
                metafields_instance.namespace = f'{metafield.namespace}'
                metafields_instance.save()
            else:
                metafields_instance = Metafield(
                    shopify_id=f'gid://shopify/Metafield/{metafield.id}',
                    key=f'{metafield.key}',
                    value=f'{value}',
                    namespace=f'{metafield.namespace}',
                )
                metafields_instance.save()
                product.metafields.append(metafields_instance)

        product.save()

        return product

    elif topic in ['customers/create', 'customers/update']:

        dataId = f"gid://shopify/Customer/{json_data.get('id', None)}"

        document = Path('flaskr/query_files/customer.graphql').read_text()
        dataInfo = shopify.GraphQL().execute(query=document,
                                             variables={"customer_id": dataId},
                                             operation_name="GetOneCustomer")
        dataInfo = json.loads(dataInfo)
        # pprint(dataInfo)
        item = flatten_data(dataInfo)
        item = recursive_replace_keys(item, key_changes)
        customer, _ = Customer.recursive_get_or_create(item)

        return customer


def flatten_data(data):
    """
    递归地移除'data'、'node'和'nodes'键，返回处理后的数据。
    """
    if isinstance(data, dict):
        if "data" in data:
            return flatten_data(data["data"])
        # elif "node" in data:
        #     return flatten_data(data["node"])
        # elif "products" in data:
        #     return flatten_data(data["products"])
        elif "nodes" in data:
            res = []
            for item in data["nodes"]:
                if flatten_data(item):
                    res.append(flatten_data(item))
            return res
        elif "node" in data:
            return flatten_data(data["node"])
        # elif "onlineStoreUrl" in data and data.get('onlineStoreUrl') is None:
        #     return None
        else:
            return {
                k: flatten_data(v) for k, v in data.items()
            # if data.get('onlineStoreUrl') is not None
            }
    elif isinstance(data, list):
        return [flatten_data(item) for item in data]
    else:
        return data


key_changes = {
    'id': 'shopify_id',
    'availablePublicationCount': 'availablePublicationsCount',
}


def recursive_replace_keys(data, key_changes):
    """
    Recursively replaces keys in a nested dictionary.

    :param data: The original dictionary with potentially nested dictionaries as values.
    :param key_changes: A dictionary mapping old keys to new keys.
    :return: A new dictionary with updated keys.
    """
    new_data = {}
    for key, value in data.items():
        # Replace the key if it is in the key_changes dictionary; otherwise, keep the original key.
        new_key = key_changes.get(key, key)
        if isinstance(value, dict):
            # Recursively apply this function to the nested dictionary.
            new_data[new_key] = recursive_replace_keys(value, key_changes)
        elif isinstance(value, list):
            # Process each item in the list recursively if it is a dictionary, otherwise just copy it.
            new_data[new_key] = [
                recursive_replace_keys(item, key_changes) if isinstance(
                    item, dict) else item for item in value
            ]
        else:
            # Simply copy the value if it is not a dictionary.
            new_data[new_key] = value
    return new_data
