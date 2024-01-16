/*
 * @Author: aaronli-uga ql61608@uga.edu
 * @Date: 2024-01-14 13:47:31
 * @LastEditors: aaronli-uga ql61608@uga.edu
 * @LastEditTime: 2024-01-15 17:01:30
 * @FilePath: /AIchatbot/app.js
 * @Description: 
 * 
 * Copyright (c) 2024 by Qi Li, All Rights Reserved. 
 */
require('dotenv').config();
const express = require('express');
const app = express();
const mongoose = require('mongoose');
const Shopify = require('shopify-api-node');

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

  
// Root Route
app.get('/', (req, res) => {
  res.send('Welcome to the NoviBOX Shopify-MongoDB Sync App');
});

// Endpoint to trigger product syncing
app.get('/Sync', async (req, res) => {
  await syncProducts();
  res.send('Products syncing to MongoDB initiated.');
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