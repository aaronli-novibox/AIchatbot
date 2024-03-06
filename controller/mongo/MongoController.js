const MongoServices = require("../../services/mongo/MongoServices")
const { MongoConnect, MongoDisconnect} = require("../../config/db.config")
const mongoose = require('mongoose')

const MongoController = {


    getProductsList: async (req, res) => {
        
        MongoConnect()
        await MongoServices.getProductsList(req, res)
        MongoDisconnect()
    }

}

module.exports = MongoController