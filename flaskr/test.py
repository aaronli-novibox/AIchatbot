from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from bson.objectid import ObjectId

if __name__ == '__main__':
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb+srv://qi:novibox2023@test.y1qqimb.mongodb.net/?retryWrites=true&w=majority")
        db = client['dev']

        # Select the collection
        collection = db['order']

        # Update documents in the collection
        result = collection.delete_many({})
        print("succeed")


    except Exception as e:
        print(f"An error occurred: {e}")
