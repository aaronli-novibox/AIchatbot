import os
from dotenv import load_dotenv

load_dotenv()
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_PASSWORD = os.getenv("SHOPIFY_API_PASSWORD")
SHOPIFY_SHOP_NAME = os.getenv("SHOPIFY_SHOP_NAME")
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_KEY = os.getenv("OPENAI_KEY")
CLUSTER_ENDPOINT = os.getenv("CLUSTER_ENDPOINT")
TOKEN = os.getenv("TOKEN")
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
