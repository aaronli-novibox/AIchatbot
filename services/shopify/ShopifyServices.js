const shopify = require('../../config/shopify.config')

const ShopifyServices = {

    getProductsList: async (req, res) =>{
        await shopify.product
                .list()
                .then((products) => res.send(products))
                .catch((err) => console.error(err));

    }

    




}

module.exports = ShopifyServices