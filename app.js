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
var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

// route
var MongoRouter = require('./routes/mongo/MongoRouter');
// var ShopifyRouter = require('./routes/shopify/');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// app.use('/', indexRouter);
// app.use('/users', usersRouter);
app.use(MongoRouter);
// app.use(ShopifyRouter);

// catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

// error handler
app.use(function (err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
