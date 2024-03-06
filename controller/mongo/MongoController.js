const MongoServices = require("../../services/mongo/MongoServices")
const { MongoConnect, MongoDisconnect} = require("../../config/db.config")
const mongoose = require('mongoose')

const MongoController = {


    getProductsList: async (req, res) => {
        
        await MongoConnect()
        console.log("sauidhksa")
        await MongoServices.getProductsList(req, res)
        await MongoDisconnect()
    }

}

module.exports = MongoController