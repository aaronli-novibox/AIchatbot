from flask import current_app, g


def webhookService(headers, json_data):

    topic = headers.get('X-Shopify-Topic')
    current_app.logger.info(topic)
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

    elif topic == 'customers/create':
        return insertCustomerToMongoDB(json_data)


def insertCustomerToMongoDB(data):

    customer = customerCreate(data)
    customerCollection(customer)

    return 1


def customerCollection(customer_data):
    customer_collection = g.db['test2']["customers"]
    customer_collection.insert_many(customer_data)

    return 1


def customerCreate(data):

    address = data.get("adress", {})
    customer = {
        "customer_id": data.get("id", None),
        "first_name": data.get("first_name", None),
        "last_name": data.get("last_name", None),
        "customer_email": data.get("email", None),
        "accepts_email_marketing": data.get("email_marketing_consent", None),
        "phone": data.get("phone", None),
        "accepts_sms_marketing": data.get("sms_marketing_consent", None),
        "total_spent": data.get("total_spent", 0.00),
        "total_orders": data.get("orders_count", 0),
        "note": data.get("note", None),
        "tax_exempt": data.get("tax_exempt", "no"),
        "tags": data.get("tags", None),
        "default_address": {
            "address1": data.get("addresses", None),
            "address2": data.get("Default Address Address2", None),
            "company": None,
            "city": address.get("Default Address City", None),
            "zip": address.get("Default Address Zip", None),
            "province": address.get("Default Address Province Code", None),
            "country": address.get("Default Address Country Code", None),
            "phone": address.get("Default Address Phone", None),
        },
    }

    return customer
