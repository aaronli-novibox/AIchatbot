from datetime import datetime, timedelta
from flaskr.product_mongo import *
from bson import SON


# update in everyday
class track_orders:

    def __init__(self) -> None:

        self.result_30 = self.retrive(30)
        self.result_60 = self.retrive(60)
        self.result_90 = self.retrive(90)

    def retrive(self, days=30):
        thirty_days_ago = datetime.now() - timedelta(days=days)
        # 生成过去30天的日期列表
        dates = [
            (thirty_days_ago + timedelta(days=i)).date() for i in range(days)
        ]
        pipeline = pipeline = pipeline = [
            {
                "$match": {
                    "closedAt": {
                        "$gte": thirty_days_ago
                    },
                    "displayFinancialStatus": {
                        "$in": ["PAID", "PARTIALLY_REFUNDED"]
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {
                            "$year": "$closedAt"
                        },
                        "month": {
                            "$month": "$closedAt"
                        },
                        "day": {
                            "$dayOfMonth": "$closedAt"
                        }
                    },
                    "total_orders": {
                        "$sum": 1
                    },
                    "unique_discount_codes": {
                        "$addToSet": "$discountCode"
                    },
                    "total_revenue": {
                        "$sum": "$totalPriceSet.shopMoney.amount"
                    },
                    'total_profit': {
                        "$sum": "$order_profit"
                    },
                    "total_quantity": {
                        "$sum": "$quantity"
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": "$_id.day"
                        }
                    },
                    "total_orders": 1,
                    "unique_discount_codes": {
                        "$ifNull": ["$unique_discount_codes", []]
                    },
                    "total_revenue": 1,
                    "total_quantity": 1,
                    "total_profit": 1
                }
            },
            {
                "$project": {
                    "date": 1,
                    "total_orders": 1,
                    "total_discount_codes": {
                        "$size": {
                            "$reduce": {
                                "input": {
                                    "$map": {
                                        "input": "$unique_discount_codes",
                                        "as": "code",
                                        "in": {
                                            "$cond": {
                                                "if": {
                                                    "$isArray": "$$code"
                                                },
                                                "then": "$$code",
                                                "else": ["$$code"]
                                            }
                                        }
                                    }
                                },
                                "initialValue": [],
                                "in": {
                                    "$setUnion": ["$$value", "$$this"]
                                }
                            }
                        }
                    },
                    "total_revenue": 1,
                    "total_quantity": 1,
                    "total_profit": 1
                }
            },
            {
                "$sort": {
                    "date": 1
                }    # 按日期排序
            }
        ]

        result = list(Order.objects.aggregate(pipeline))

        # 将结果转换为字典，键为日期，值为聚合结果
        result_dict = {item['date'].date(): item for item in result}

        # 初始化结果列表
        total_orders_list = []
        unique_discount_codes_list = []
        total_quantity_list = []
        total_revenue_list = []
        total_profit_list = []

        # 遍历过去30天的日期
        for date in dates:
            if date in result_dict:
                total_orders_list.append(result_dict[date]['total_orders'])
                unique_discount_codes_list.append(
                    result_dict[date]['total_discount_codes'])
                total_quantity_list.append(result_dict[date]['total_quantity'])
                total_revenue_list.append(result_dict[date]['total_revenue'])
                total_profit_list.append(result_dict[date]['total_profit'])

            else:
                total_orders_list.append(0)
                unique_discount_codes_list.append(0)
                total_quantity_list.append(0)
                total_revenue_list.append(0)
                total_profit_list.append(0)

        return {
            "orders": total_orders_list,
            "influencers": unique_discount_codes_list,
            "product_sold": total_quantity_list,
            "revenues": total_revenue_list,
            "profits": total_profit_list
        }, 200

    def top_seller(self, days=30):
        # 获取过去30天内的订单
        thirty_days_ago = datetime.now() - timedelta(days)

        pipeline = [
            {
                "$match": {
                    "closedAt": {
                        "$gte": thirty_days_ago
                    }
                }
            },
            {
                "$unwind": "$lineitem"
            },
            {
                "$lookup": {
                    "from": "line_item",
                    "localField": "lineitem",
                    "foreignField": "_id",
                    "as": "lineitem_details"
                }
            },
            {
                "$unwind": "$lineitem_details"
            },
            {
                "$group": {
                    "_id": "$lineitem_details.lineitem_sku",
                    "totalQuantitySold": {
                        "$sum": "$lineitem_details.lineitem_quantity"
                    }
                }
            },
            {
                "$sort": {
                    "totalQuantitySold": -1    # 按卖出数量降序排序
                }
            }
        ]

        # 执行聚合管道
        result = Order.objects.aggregate(pipeline)

        return list(result)

    def sales_chart(self, promo_code, days):

        influencer = Influencer.objects(promo_code=promo_code).first()

        if influencer is None:
            return {"message": "Influencer not found"}, 400

        # 获取过去30天内的订单
        thirty_days_ago = datetime.now() - timedelta(days)
        print(thirty_days_ago)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "_id": influencer.id,
                }
            },
            {
                "$unwind": "$orders"
            },
            {
                "$lookup": {
                    "from": "order",    # Order 类对应的集合名称
                    "localField": "orders.order",
                    "foreignField": "_id",
                    "as": "order_details"
                }
            },
            {
                "$unwind": "$order_details"
            },
            {
                "$match": {
                    "order_details.closedAt": {
                        "$gte": thirty_days_ago
                    },
                    "order_details.displayFinancialStatus": {
                        "$in": ["PAID", "PARTIALLY_REFUNDED"]
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {
                            "$year": "$order_details.closedAt"
                        },
                        "month": {
                            "$month": "$order_details.closedAt"
                        },
                        "day": {
                            "$dayOfMonth": "$order_details.closedAt"
                        }
                    },
                    "total_orders": {
                        "$sum": 1
                    },
                    "total_profit": {
                        "$sum": "$order_details.order_profit"
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": "$_id.day"
                        }
                    },
                    "total_orders": 1,
                    "total_profit": 1,
                }
            },
            {
                "$sort": {
                    "date": 1
                }
            }
        ]

        # 执行聚合管道
        result = list(Influencer.objects.aggregate(pipeline))
        # 将结果转换为字典，以便快速查找
        result_dict = {
            item['date'].strftime('%Y-%m-%d'): item for item in result
        }
        # 生成过去30天的日期列表
        dates = [(thirty_days_ago + timedelta(days=i)).strftime('%Y-%m-%d')
                 for i in range(days)]

        # 初始化结果列表
        total_orders_list = []
        total_profit = []

        # 遍历过去30天的日期
        for date in dates:
            if date in result_dict:
                total_orders_list.append(result_dict[date]['total_orders'])
                total_profit.append(result_dict[date]['total_profit'])
            else:
                total_orders_list.append(0)
                total_profit.append(0)

        # 打印结果
        print("Total Orders List:", total_orders_list)
        print("Total Commission List:", total_profit)

        return {
            "orders": total_orders_list,
            "revenues": total_profit,
        }, 200

    def product_sold(self, promo_code, days):

        influencer = Influencer.objects(promo_code=promo_code).first()

        # 获取过去30天内的订单
        thirty_days_ago = datetime.now() - timedelta(days)

        if influencer is None:
            return {"message": "Influencer not found"}, 400

        pipeline = [
            {
                "$match": {
                    "_id": influencer.id
                }
            },
            {
                "$unwind": "$orders"
            },
            {
                "$lookup": {
                    "from": "order",    # Order 类对应的集合名称
                    "localField": "orders.order",
                    "foreignField": "_id",
                    "as": "order_details"
                }
            },
            {
                "$unwind": "$order_details"
            },
            {
                "$match": {
                    "order_details.closedAt": {
                        "$gte": thirty_days_ago
                    },
                    "order_details.displayFinancialStatus": {
                        "$in": ["PAID", "PARTIALLY_REFUNDED"]
                    }
                }
            },
            {
                "$unwind": "$order_details.lineitem"
            },
            {
                "$lookup": {
                    "from": "line_item",
                    "localField": "order_details.lineitem",
                    "foreignField": "_id",
                    "as": "lineitem_details"
                }
            },
            {
                "$unwind": "$lineitem_details"
            },
            {
                "$group": {
                    "_id": "$lineitem_details.lineitem_sku",
                    "total_quantity": {
                        "$sum": "$lineitem_details.lineitem_quantity"
                    },
                    "total_profit": {
                        "$sum": "$lineitem_details.profit"
                    },
                    "commissions": {
                        "$sum": "$lineitem_details.commission_fee"
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "product": "$_id",
                    "total_quantity": 1,
                    "total_profit": 1,
                    "commissions": 1
                }
            }
        ]

        # 执行聚合管道

        result = list(Influencer.objects.aggregate(pipeline))

        # 打印结果
        for item in result:
            print(f"Product: {item['product']}")
            print(f"Total Quantity: {item['total_quantity']}")
            print(f"Total Commission Fee: {item['total_profit']}")
            print(f"Commissions: {item['commissions']}")
            print()

        return {"products": result}, 200

    def related(self, promo_code):
        influencer = Influencer.objects(promo_code=promo_code).first()

        if influencer is None:
            return {"message": "Influencer not found"}, 400

        data = {
            'total_gmv': influencer.total_commission,
            'total_orders_sold': influencer.order_nums,
            'total_products_sold': influencer.product_nums,
            'total_promo_codes_used': influencer.promo_code_used,
        }

        return data, 200

    # add product contract
    # start_time, end_time, commisson_rate, influencer  _username和product啥信息发过去可以确定是哪个product，然后influencer可以把product记在合同里就加个add的api
    def product_contract(self, start_time, end_time, commission_rate,
                         promo_code, product_sid):
        product = Product.objects(shopify_id=product_sid).first()
        influencer = Influencer.objects(promo_code=promo_code).first()

        if product is None:
            return {"message": "Product not found"}, 400

        if influencer is None:
            return {"message": "Influencer not found"}, 400

        influencer_product = InfluencerProduct(
            product=product,
            product_contract_start=start_time,
            product_contract_end=end_time,
            commission=commission_rate)

        if influencer_product not in influencer.product:
            influencer.product.append(influencer_product)
        else:
            # 如果已经存在，更新合同信息
            influencer.product[influencer.product.index(
                influencer_product)] = influencer_product

        influencer.save()

        return {"message": "Product contract added"}, 200

    # update product contract
    # start_time, end_time, commisson_rate, influencer
    def update_contract(self, start_time, end_time, commission_rate, promo_code,
                        product_sid):
        product = Product.objects(shopify_id=product_sid).first()
        influencer = Influencer.objects(promo_code=promo_code).first()

        if product is None:
            return {"message": "Product not found"}, 400

        if influencer is None:
            return {"message": "Influencer not found"}, 400

        influencer_product = None
        for ip in influencer.product:
            if ip.product == product:
                influencer_product = ip
                break

        if influencer_product is None:
            return {"message": "Contract not found"}, 400

        influencer_product.pre_commission = influencer_product.commission
        influencer_product.commission = commission_rate
        influencer_product.product_contract_start = start_time
        influencer_product.product_contract_end = end_time
        influencer_product.review_status = "Reviewing"

        influencer.save()
        return {"message": "Product contract updated"}, 200

    def review_contract(self,
                        promo_code,
                        product_sid,
                        review_result,
                        clean=False):
        product = Product.objects(shopify_id=product_sid).first()
        influencer = Influencer.objects(promo_code=promo_code).first()

        if product is None:
            return {"message": "Product not found"}, 400

        if influencer is None:
            return {"message": "Influencer not found"}, 400

        influencer_product = None
        for ip in influencer.product:
            if ip.product == product:
                influencer_product = ip
                break

        if influencer_product is None:
            return {"message": "Contract not found"}, 400

        if clean:
            influencer_product.pre_commission = ""
            influencer_product.review_status = ""
        else:
            if review_result:
                influencer_product.review_status = "Success"
            else:
                influencer_product.review_status = "Failed"
                influencer_product.commission = influencer_product.pre_commission

        influencer.save()
        return {"message": "Product contract reviewed/updated"}, 200
