from flask import g, current_app


# return cursor type, and filter '_id' field
def getProductListFromMongoDB():
    product_collection = g.db['test']["product"]
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
