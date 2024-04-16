from flask import g, current_app


# return cursor type, and filter '_id' field
def getProductListFromMongoDB():
    product_collection = g.db['test2']["products"]
    documents = product_collection.find({}, {'_id': 0, 'description_vector': 0})

    return documents


def getOrderListFromMongoDB():
    order_collection = g.db['test2']["orders"]
    documents = order_collection.find({}, {'_id': 0})

    return documents


def getCustomerListFromMongoDB():

    customer_collection = g.db['test2']["customers"]
    documents = customer_collection.find({}, {'_id': 0})

    return documents


def getInfluencerListFromMongoDB():

    customer_collection = g.db['test2']["influencers"]
    documents = customer_collection.find({}, {'_id': 0})

    return documents

def getNewInfluencerListFromMongoDB():

    influencer_collection = g.db['test2']["new_influencers"]

    return influencer_collection


def insertInfluencerData(influencer_data):

    promo_codes = [data['promo_code'] for data in influencer_data]

    influencer_collection = g.db['test2']["influencers"]
    influencer_collection.insert_many(influencer_data)

    for code in promo_codes:
        if influencer_collection.find_one({"promo_code": code}):
            print(f"Duplicate promo code found: {code}. Aborting operation.")
            return 0

    else:
        influencer_collection.insert_many(influencer_data)
        print("Data inserted successfully.")
        return 1
