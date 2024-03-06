
const ShopifyServices = require("../../services/shopify/ShopifyServices")

const ShopifyController = {

    getProductsList: async (req, res) => {
        ShopifyServices.getProductsList(req, res)
    }

}

module.exports = ShopifyServices