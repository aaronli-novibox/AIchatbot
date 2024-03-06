const mongoose = require("mongoose")
const Schema = mongoose.Schema

const DataType = {

    product_id: {
        type: String,
        required: true,
        unique: true
    },

    variants_id: {
        type: String,
    },

    vendor: {
        type: String,
        // default: "NOVI BOX",
    },

    product_type: {
        type: String,
    },

    title: {
        type: String,
    },

    variant_title: {
        type: String,
    },

    price: {
      type: Number,
    },

    sku: {
      type: String,
    },

    weight: {
      type: Number,  
    },

    weight_unit: {
        type: String,
    },

    grams: {
        type: Number,
    },

    inventory_item_id: {
        type: String,    
    },

    inventory_quantity: {
        type: Number,
    }

}

const ProductModel = mongoose.model("product", new Schema(DataType), 'product')

module.exports = ProductModel