/*
 * @Author: aaronli-uga ql61608@uga.edu
 * @Date: 2024-01-23 13:15:40
 * @LastEditors: aaronli-uga ql61608@uga.edu
 * @LastEditTime: 2024-01-24 16:15:43
 * @FilePath: /novibox/webhook.js
 * @Description: 
 * 
 * Copyright (c) 2024 by Qi Li, All Rights Reserved. 
 */
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const app = express();
const PORT = 3000;

// Replace 'shared_secret' with your Shopify app's shared secret
const SHOPIFY_SECRET = 'shared_secret';

app.use(bodyParser.json({
  verify: (req, res, buf) => {
    req.rawBody = buf;
  }
}));

// Webhook endpoint
app.post('/webhook/products/update', (req, res) => {
  const hmac = req.get('X-Shopify-Hmac-Sha256');
  const hash = crypto.createHmac('sha256', SHOPIFY_SECRET)
                     .update(req.rawBody, 'utf8', 'hex')
                     .digest('base64');

  if (hash === hmac) {
    console.log('Webhook verified');
    // Log the product information
    console.log(req.body);

    res.status(200).send('Webhook received');
  } else {
    console.log('Webhook verification failed');
    res.status(403).send('Unauthorized');
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
