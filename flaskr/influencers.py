from datetime import datetime, timedelta
from flaskr.product_mongo import *


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
        pipeline = [
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
                    "total_commission": {
                        "$sum": "$order_commission_fee"
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
                    "total_discount_codes": {
                        "$size": {
                            "$reduce": {
                                "input": "$unique_discount_codes",
                                "initialValue": [],
                                "in": {
                                    "$setUnion": ["$$value", "$$this"]
                                }
                            }
                        }
                    },
                    "total_commission": 1,
                    "total_quantity": 1
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
        total_commission_list = []

        # 遍历过去30天的日期
        for date in dates:
            if date in result_dict:
                total_orders_list.append(result_dict[date]['total_orders'])
                unique_discount_codes_list.append(
                    result_dict[date]['total_discount_codes'])
                total_quantity_list.append(result_dict[date]['total_quantity'])
                total_commission_list.append(
                    result_dict[date]['total_commission'])
            else:
                total_orders_list.append(0)
                unique_discount_codes_list.append(0)
                total_quantity_list.append(0)
                total_commission_list.append(0)

        return {
            "orders": total_orders_list,
            "influencers": unique_discount_codes_list,
            "product_sold": total_quantity_list,
            "revenues": total_commission_list,
        }
