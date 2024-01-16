/*
 * @Author: aaronli-uga ql61608@uga.edu
 * @Date: 2024-01-14 13:47:31
 * @LastEditors: aaronli-uga ql61608@uga.edu
 * @LastEditTime: 2024-01-15 22:09:30
 * @FilePath: /AIchatbot/app.js
 * @Description: 
 * 
 * Copyright (c) 2024 by Qi Li, All Rights Reserved. 
 */
require('dotenv').config();
const express = require('express');
const app = express();
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

const client = new MongoClient(MONGO_URI);

  
// Root Route
app.get('/', (req, res) => {
  res.send('Welcome to the NoviBOX Shopify-MongoDB Sync App');
});

// Endpoint to trigger product syncing
app.get('/mongo', async (req, res) => {
    try {
      const database = client.db('test');
      const movies = database.collection('product');
      // Query for a movie that has the title 'Back to the Future'
      const query = { name: 'duck lamp' };
      const movie = await movies.find(query);
      for await (const doc of movie) {
        console.log(doc);
      }
    } finally {
      // Ensures that the client will close when you finish/error
      await client.close();
    }
});

// Endpoint to trigger product syncing
app.get('/products', async (req, res) => {
  await shopify.product
    .list()
    .then((products) => res.send(products))
    .catch((err) => console.error(err));
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
})