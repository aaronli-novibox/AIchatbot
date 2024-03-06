const mongoose = require('mongoose');
const path = require('path')
const { MONGO_URI } = require('../config/config')


async function MongoConnect () {

    await mongoose.connect(MONGO_URI,)
    .then(() => {
        console.log('Connected to MongoDB: ', mongoose.connection.db.databaseName);
    })
    .catch((err) => {
        console.error('Error connecting to MongoDB:', err);
    });

}

async function MongoDisconnect () {
    await mongoose.disconnect()
    .then(() => {
        console.log('Disconnected from MongoDB');
    })
    .catch((err) => {
        console.error('Error disconnecting from MongoDB:', err);
    })
}

module.exports = {MongoConnect, MongoDisconnect}


