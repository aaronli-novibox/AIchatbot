from datetime import datetime, timedelta
from flaskr.product_mongo import *


# update in everyday
class track_orders:

    def __init__(self) -> None:

        self.result_30 = self.retrive(30)
        self.result_60 = self.retrive(60)

    def retrive(self, days=30):
        thirty_days_ago = datetime.now() - timedelta(days=days)
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
                        "$size": "$unique_discount_codes"
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

        return list(Order.aggregate(pipeline))
