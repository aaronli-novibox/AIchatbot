/*
 * @Author: aaronli-uga ql61608@uga.edu
 * @Date: 2024-01-07 17:27:53
 * @LastEditors: aaronli-uga ql61608@uga.edu
 * @LastEditTime: 2024-01-08 17:28:35
 * @FilePath: /AIchatbot/main.js
 * @Description: 
 * 
 * Copyright (c) 2024 by Qi Li, All Rights Reserved. 
 */
require('dotenv').config();
const Shopify = require('shopify-api-node');
const { MongoClient } = require('mongodb');

// Shopify API Initialization
const shopify = new Shopify({
  shopName: process.env.SHOP_NAME,
  apiKey: process.env.SHOPIFY_API_KEY,
  password: process.env.SHOPIFY_API_PASSWORD
});

// MongoDB Connection
const uri = process.env.MONGODB_ATLAS_URI;
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function main() {
  try {
    await client.connect();
    const database = client.db('shopifyData');
    const productsCollection = database.collection('products');

    // Fetch products from Shopify
    const products = await shopify.product.list();

    // Process and store each product
    for (const product of products) {
      // Example of adding embedding info (this would depend on the AI model)
      product.embeddingInfo = someAIModel.process(product);

      // Store in MongoDB
      await productsCollection.updateOne(
        { id: product.id },
        { $set: product },
        { upsert: true }
      );
    }
  } catch (e) {
    console.error(e);
  } finally {
    await client.close();
  }
}

main().catch(console.error);

function someAIModel.process(product) {
  // Placeholder for AI processing logic
  // Return embedding or processed data
  return {}; // Replace with actual embedding data
}
