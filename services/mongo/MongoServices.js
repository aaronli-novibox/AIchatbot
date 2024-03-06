
const ProductModel = require("../../model/mongo/MongoModel")
const mongoose = require("mongoose")
const MongoServices = {
    
    getProductsList: async (req, res) => {
        
        // query should be connected with req
        // const query = { name: 'duck lamp' };
        let products = await ProductModel.find({})

        res.json({
            code: '0000',
            msg: 'success',
            data: {
                products
            }
        })

    }

}

module.exports = MongoServices