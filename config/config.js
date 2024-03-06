require('dotenv').config();
const {
    MONGO_URI,
    SHOPIFY_API_KEY,
    SHOPIFY_API_PASSWORD,
    SHOPIFY_SHOP_NAME
} = process.env;

module.exports = {
    MONGO_URI,
    SHOPIFY_API_KEY,
    SHOPIFY_API_PASSWORD,
    SHOPIFY_SHOP_NAME
}
