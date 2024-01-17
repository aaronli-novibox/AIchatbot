/*
 * @Author: aaronli-uga ql61608@uga.edu
 * @Date: 2024-01-16 14:03:30
 * @LastEditors: aaronli-uga ql61608@uga.edu
 * @LastEditTime: 2024-01-17 14:48:55
 * @FilePath: /AIchatbot/test_sync.js
 * @Description: 
 * 
 * Copyright (c) 2024 by Qi Li, All Rights Reserved. 
 */
require('dotenv').config();
const Shopify = require('shopify-api-node');
const { MongoClient } = require('mongodb')

// Environment variables
const {
    MONGO_URI,
    SHOPIFY_API_KEY,
    SHOPIFY_API_PASSWORD,
    SHOPIFY_SHOP_NAME
} = process.env;

// Shopify API client
const shopify = new Shopify({
    shopName: SHOPIFY_SHOP_NAME,
    apiKey: SHOPIFY_API_KEY,
    password: SHOPIFY_API_PASSWORD
});




async function syncShopifyDataToMongoDB() {
    try{
        const client = new MongoClient(MONGO_URI);
        await client.connect()

        const db = client.db('test');
        const collection = db.collection('product')

        const products = await shopify.product.list();
        for (const product of products){
            for (const variant of product.variants){
                const document = {
                    product_id: String(product.id),
                    variants_id: String(variant.id),
                    vendor: product.vendor,
                    product_type: product.product_type,
                    title: product.title,
                    variant_title: variant.title,
                    price: parseFloat(variant.price),
                    sku: variant.sku,
                    weight: parseFloat(variant.weight),
                    weight_unit: variant.weight_unit,
                    grams: parseFloat(variant.grams),
                    inventory_item_id: String(variant.inventory_item_id),
                    inventory_quantity: parseInt(variant.inventory_quantity),
                }

                await collection.insertOne(document);
            }
        }
        console.log('Data sync completed.');
        client.close();
    } catch (error){
        console.error('Error:', error);
    }
}

syncShopifyDataToMongoDB();