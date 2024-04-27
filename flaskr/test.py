from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

if __name__ == '__main__':
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb+srv://qi:novibox2023@test.y1qqimb.mongodb.net/?retryWrites=true&w=majority")
        db = client['test2']

        hashed_password = generate_password_hash("11112222", method='pbkdf2:sha256')

        # Define the aggregation pipeline for copying the collection
        pipeline = [
            {"$match": {}},  # Match all documents
            {"$addFields": {
                "first_name": "",  # Placeholder for first name
                "middle_name": "",  # Placeholder for middle name
                "last_name": "",  # Placeholder for last name
                "country": "",  # Placeholder for country
                "city_state": "",  # Placeholder for city and state
                "age": "",  # Placeholder for age
                "audience": [],  # Placeholder for age
                "phone": "",  # Placeholder for phone number
                "shipping_address": "",  # Placeholder for shipping address
                "collaboration": [],  # Placeholder for collaboration, expecting an array
                "niche": [],
                "interest": [],
                "password": hashed_password,
                "type":"",
                "bio": "",
                "avatar": None,
                "role": "influencer"  # Set default role to "influencer"
            }},
            {"$out": "new_influencers"}  # Output to new collection
        ]

        # Execute the aggregation pipeline to copy 'influencers' to 'new_influencers'
        db["influencers"].aggregate(pipeline)

        # Insert a new influencer with admin role
        admin_password = generate_password_hash("123456", method='pbkdf2:sha256')
        db["new_influencers"].insert_one({
            "influencer_name": "admin",
            "influencer_email": "admin@fakeemail.com",
            "promo_code": "ADMIN_NOVBOX_0",
            'contract_start': None,
            'contract_end': None,
            'product': [],
            "password": admin_password,
            "role": "admin",
            "first_name": "admin",  # Placeholder for first name
            "middle_name": "",  # Placeholder for middle name
            "last_name": "",  # Placeholder for last name
            "country": "US",  # Placeholder for country
            "city_state": "",  # Placeholder for city and state
            "type": "",
            "age": "",  # Placeholder for age
            "audience": [],
            "phone": "",  # Placeholder for phone number
            "shipping_address": "",  # Placeholder for shipping address
            "collaboration": [],  # Placeholder for collaboration, expecting an array
            "niche": [],
            "interest": [],
            "avatar": None,
            "bio": "",
        })

        # Insert a new influencer with influencer role
        admin_password = generate_password_hash("123456", method='pbkdf2:sha256')
        db["new_influencers"].insert_one({
            "influencer_name": "Hula",
            "influencer_email": "mengzhimin5@gmail.com",
            "promo_code": "ADMIN_NOVBOX_0",
            'contract_start': None,
            'contract_end': None,
            'product': [],
            "password": hashed_password,
            "role": "influencer",
            "first_name": "admin",  # Placeholder for first name
            "middle_name": "",  # Placeholder for middle name
            "last_name": "",  # Placeholder for last name
            "country": "US",  # Placeholder for country
            "city_state": "",  # Placeholder for city and state
            "age": "",  # Placeholder for age
            "type": "",
            "audience": [],
            "phone": "",  # Placeholder for phone number
            "shipping_address": "",  # Placeholder for shipping address
            "collaboration": [],  # Placeholder for collaboration, expecting an array
            "niche": [],
            "interest": [],
            "avatar": None,
            "bio": "",
        })

        print("Influencers table copied to new collection 'new_influencers' and admin added.")
    except Exception as e:
        print(f"An error occurred: {e}")
