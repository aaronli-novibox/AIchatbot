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
        collection = db['product']

        # Define the filter with ObjectId
        filter = {"_id": ObjectId('662c5ed5c5e9da8462eb2b49')}

        # Find the document
        document = collection.find_one(filter)

        # Print the document
        if document:
            print(document)
        else:
            print("No document found with the given _id.")

    except Exception as e:
        print(f"An error occurred: {e}")
