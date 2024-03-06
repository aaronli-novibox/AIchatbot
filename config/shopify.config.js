const { SHOPIFY_API_KEY, SHOPIFY_API_PASSWORD, SHOPIFY_SHOP_NAME } = require('./config')
const Shopify = require('shopify-api-node');

const shopify = new Shopify({
    shopName: SHOPIFY_SHOP_NAME,
    apiKey: SHOPIFY_API_KEY,
    password: SHOPIFY_API_PASSWORD
});

module.exports = shopify