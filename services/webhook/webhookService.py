from flask import current_app, g


def webhookService(headers, json_data):

    topic = headers.get('X-Shopify-Topic')

    current_app.logger.info(json_data)

    if topic == 'orders/create':
        return orderCreate(req)

    elif topic == 'orders/updated':
        return orderUpdate(req)

    elif topic == 'orders/delete':
        return orderDelete(req)

    elif topic == 'products/create':
        return productCreate(req)

    elif topic == 'products/update':
        return productUpdate(req)

    elif topic == 'products/delete':
        return productDelete(req)


def orderCreate(req):
    data = req.get_json()

    current_app.logger.info(data)
