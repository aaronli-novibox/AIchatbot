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
                "password": hashed_password,
                "role": "editor"  # Set default role to "editor"
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
            "role": "admin"
        })

        print("Influencers table copied to new collection 'new_influencers' and admin added.")
    except Exception as e:
        print(f"An error occurred: {e}")
