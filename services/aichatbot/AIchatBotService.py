import pprint
from flask import g, current_app, jsonify
from FlagEmbedding import FlagModel
import numpy as np
import re
import os
import shopify
from pathlib import Path
import json
import time
import redis
from flaskr.product_mongo import *
from .redisServer import *


def flatten_data(data):
    """
    递归地移除'data'、'node'和'nodes'键，返回处理后的数据。
    """
    if isinstance(data, dict):
        if "data" in data:
            return flatten_data(data["data"])
        # elif "node" in data:
        #     return flatten_data(data["node"])
        # elif "products" in data:
        #     return flatten_data(data["products"])
        elif "nodes" in data:
            res = []
            for item in data["nodes"]:
                if flatten_data(item):
                    res.append(flatten_data(item))
            return res
        elif "onlineStoreUrl" in data and data.get('onlineStoreUrl') is None:
            return None
        else:
            return {
                k: flatten_data(v) for k, v in data.items()
            # if data.get('onlineStoreUrl') is not None
            }
    elif isinstance(data, list):
        return [flatten_data(item) for item in data]
    else:
        return data


# 匹配branch
def matchBranch(text):
    patterns = [
        (r'1', 1
        ),    # The user's input is a description of the goods they need to purchase, and we will make recommendations based on the user's input next.
        (r'2', 2
        ),    #  The user wants to query historical order information, logistics information, etc.
        (r'3', 3),    #  The user is using our conversation for casual chat.
        (r'4', 4)    #  Unable to identify user intent.
    ]

    for pattern, branch in patterns:
        if re.search(pattern, text):
            return branch

    return None


# 进入AIchatbot，直接输入
def userTyping(req):

    # get the user's typing
    user_typing = req["user_typing"]

    # 根据user_Need_List动态生成描述内容的Python代码
    content = 'You are a problem classifier with the following possible categories: 1. Using AI Swipe to browse products: This may allow users to browse products using an AI-driven recommendation system, potentially including swipe options to quickly like or dislike, similar to many modern dating apps. This mode is usually for selecting gifts for oneself. 2. Using AI to find gifts: This option can provide AI-recommended gift selection help, possibly using information entered by the user about the recipient to suggest suitable gift options. This mode is usually for selecting gifts for others. 3. Contact Us: This is a standard customer service feature, where users can contact support staff for inquiries or assistance. This also includes inquiries related to business cooperation. 4. Order Help: This option may provide support related to orders, such as tracking delivery, managing returns, or resolving any issues that arose during order placement. 5. Small Talk: User inputs that are unrelated to the four above categories. Your output needs to maintain the following format, setting the classification you determine as True: { "AI Swipe": false, "Using AI to find gifts": false, "Contact Us": true, "Order Help": false, "Small Talk": false } You need to return the entire JSON, including the false parts. Your output should only contain this JSON, with no extra text output.'

    content += f'The user\'s input is: "{user_typing}". Please classify the user\'s input.'

    stream = g.clientOpenAI.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": content
        }],
        stream=True,
    )

    # match the user flow's branch
    typing_string_ = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            typing_string_ = typing_string_ + chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end='')

    typing_string_ = json.loads(typing_string_)
    return {'code': '0000', 'data': typing_string_, 'msg': 'success'}, 200

    # branch_index = matchBranch(typing_string_)

    # if branch_index == 1:

    #     return {'code': '0001', 'msg': 'AI'}

    # elif branch_index == 2:

    #     # 这里跳转到历史订单查询的代码
    #     return {
    #         'code':
    #             '0002',    # '0002'代表请求查询历史订单信息等
    #         'data': {
    #             'result': None,
    #         },
    #         'msg':
    #             'The user wants to query historical order information, logistics information, etc. 请求查询历史订单信息等'
    #     }, 200

    # elif branch_index == 3:

    #     # 这里跳转到闲聊的代码
    #     return {
    #         'code': '0003',    # '0003'代表用户在使用我们的对话进行闲聊
    #         'data': {
    #             'result': None,
    #         },
    #         'msg': 'The user is using our conversation for casual chat. 请求闲聊'
    #     }, 200

    # elif branch_index == 4:

    #     # 这里跳转到提示用户输入的代码
    #     return {
    #         'code': '0004',    # '0004'代表无法识别用户意图
    #         'data': {
    #             'result': None,
    #         },
    #         'msg': 'Unable to identify user intent. 搞不懂用户请求'
    #     }, 200


# 根据用户的聊天框输入推荐礼物
def recommandGiftByUserInput(req, clientip):

    user_typing = req["user_typing"]

    history_gift = get_recommanded_gifts(clientip)

    content = f'''Here is a user's input:"{user_typing}", give me a list of 10 terms to describe the potential product. You must include the products mentioned in the input.'''

    stream = g.clientOpenAI.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": content
        }],
        stream=True,
    )

    # match the user flow's branch
    typing_string_ = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            typing_string_ = typing_string_ + chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end='')

    # 初始化 FlagModel
    emb_model = current_app.config['MODEL']

    query_vector = emb_model.encode(typing_string_).astype(np.float64).tolist()

    # 构建聚合查询
    query = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "descriptionVector",
                "queryVector": query_vector,
                "numCandidates": 50,
                "limit": 20
            }
        },
        {
            "$match": {
                "status": "ACTIVE",    # 先筛选状态为ACTIVE的文档
                "_id": {
                    "$nin": history_gift
                }    # 排除已推荐的礼物
            }
        },
        {
            "$addFields": {
                "similarityScore": {
                    "$meta": "vectorSearchScore"
                },
            }
        },
        {
            "$lookup": {
                "from": "product_variant",
                "localField": "variants",
                "foreignField": "_id",
                "as": "variantDetails"
            }
        },
        {
            "$addFields": {
                "firstVariantId": {
                    "$arrayElemAt": ["$variantDetails.shopify_id",
                                     0]    # 获取variantDetails数组中的第一个元素的_id
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "ids": {
                    "$push": "$_id"
                },
                "details": {
                    "$push": {
                        "description": "$description",
                        "featureImage": "$featureImage",
                        "shopify_id": "$shopify_id",
                        "onlineStoreUrl": "$onlineStoreUrl",
                        "priceRangeV2": "$priceRangeV2",
                        "tags": "$tags",
                        "title": "$title",
                        "productType": "$productType",
                        "featuredImage": "$featuredImage",
                        "firstVariantId": "$firstVariantId"
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,    # 隐藏 _id 字段
                "ids": 1,
                "details": 1
            }
        }
    ]

    # 执行查询
    # results = g.db.dev.product.aggregate(query)
    results_dict = Product.objects.aggregate(query)
    results_dict = dict(results_dict)
    current_app.logger.info(results_dict)
    new_recommand_gifts, results = results_dict['ids'], results_dict['details']

    current_app.logger.info(new_recommand_gifts)

    add_recommand_gift(clientip, new_recommand_gifts)
    # 假设 results 是从 MongoDB 查询得到的结果
    results_list = list(results)    # 将 CommandCursor 对象转换为列表

    # 成功返回
    return {
        'code':
            '0000',
        'data': {
            'result': results_list,
        },
        'msg':
            'The user\'s input is a description of the goods they need to purchase, and recommand success. 请求推荐礼物, 推荐成功'
    }, 200


# 根据用户提供的信息推荐礼物
def recommandGiftByList(req):

    # get the user's input: relationship, interests, style are optional, if not provided, use default values
    gender = req.get("gender")
    occasion = req.get("occasion")
    budget = req.get("budget")
    age = req.get("age")

    if gender is None or occasion is None or budget is None or age is None:
        return {
            'code':
                '0001',
            'data': {
                'result': None,
            },
            'msg':
                'The user\'s input is incomplete. Please provide the necessary information and try again. 用户输入不完整，请提供必要信息后重试'
        }, 200

    relationship = req.get("relationship", None)    # 如果不存在，则返回 None
    interests = req.get("interests", None)    # 如果不存在，则返回 None
    style = req.get("style", None)    # 如果不存在，则返回 None

    # 初始化 FlagModel
    emb_model = current_app.config['MODEL']

    # 构建内容的各个部分
    parts = [f"A product suitable for {age} {gender} individuals"]

    if interests:
        # Check if interests is a list and has multiple items
        if isinstance(interests, list):
            if len(interests) > 1:
                formatted_interests = ", ".join(
                    interests[:-1]) + " and " + interests[-1]
            else:
                formatted_interests = interests[0]
        else:
            formatted_interests = interests    # assuming interests is a single string or similar

        parts.append(f", who are interested in {formatted_interests}")

    parts.append(f" and looking for something for {occasion}.")

    if budget:
        parts.append(f" Considering the budget is {budget}")

    if relationship is not None:
        parts.append(f", and it's meant for {relationship} relationships.")
    else:
        parts.append(".")

    if style is not None:
        parts.append(f" The preferred style is {style}.")

    # 将所有部分组合成最终的内容字符串
    content = "".join(
        parts
    ) + " How would you describe such a product? Please provide a description that captures the essence of these criteria."

    # 定义价格范围
    if budget == "<$20":
        price_min = 0
        price_max = 20
    elif budget == "$20-$50":
        price_min = 20
        price_max = 50
    elif budget == "$50-$100":
        price_min = 50
        price_max = 100
    elif budget == "$100-$200":
        price_min = 100
        price_max = 200
    elif budget == "Above $200":
        price_min = 200
        # 为 price_max 设置一个高值，或者可以根据应用场景决定是否需要上限
        price_max = 1000000    # 假设作为一个高的上限值

    print(f"Price range: {price_min} to {price_max}")

    results_list = []

    stream = g.clientOpenAI.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": content
        }],
        stream=True,
    )
    project_string_ = ""
    # print("I guess you need the commodity that\n")

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            project_string_ = project_string_ + chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end='')

    query_vector = emb_model.encode(project_string_).astype(np.float64).tolist()

    # 构建聚合查询
    query = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "descriptionVector",
                "queryVector": query_vector,
                "numCandidates": 50,
                "limit": 20
            }
        },
        {
            "$match": {
                "priceRangeV2.minVariantPrice.currencyCode": "USD",
                "priceRangeV2.maxVariantPrice.currencyCode": "USD",
                "priceRangeV2.minVariantPrice.amount": {
                    "$gte": price_min
                },
                "priceRangeV2.maxVariantPrice.amount": {
                    "$lte": price_max
                },
                "status": "ACTIVE"
            }
        },
        {
            "$lookup": {
                "from": "product_variant",
                "localField": "variants",
                "foreignField": "_id",
                "as": "variantDetails"
            }
        },
        {
            "$lookup": {
                "from": "product_option",
                "localField": "options",
                "foreignField": "_id",
                "as": "optionsDetails"
            }
        },
        {
            "$lookup": {
                "from": "metafield",
                "localField": "metafields",
                "foreignField": "_id",
                "as": "metafieldsDetails"
            }
        },
        {
            "$addFields": {
                "similarityScore": {
                    "$meta": "vectorSearchScore"
                },
                "allVariantsUnavailable": {
                    "$allElementsTrue": {
                        "$map": {
                            "input": "$variantDetails",
                            "as": "variant",
                            "in": {
                                "$not": "$$variant.availableForSale"
                            }
                        }
                    }
                },
                "ratingValue": {
                    "$let": {
                        "vars": {
                            "filteredMetafields": {
                                "$filter": {
                                    "input": "$metafieldsDetails",
                                    "as": "metafield",
                                    "cond": {
                                        "$and": [{
                                            "$eq": [
                                                "$$metafield.key", "ratingValue"
                                            ]
                                        }, {
                                            "$eq": [
                                                "$$metafield.namespace",
                                                "vitals"
                                            ]
                                        }]
                                    }
                                }
                            }
                        },
                        "in": {
                            "$ifNull": [{
                                "$arrayElemAt": [
                                    "$$filteredMetafields.value", 0
                                ]
                            }, None]
                        }
                    }
                },
                "reviewCount": {
                    "$let": {
                        "vars": {
                            "filteredMetafields": {
                                "$filter": {
                                    "input": "$metafieldsDetails",
                                    "as": "metafield",
                                    "cond": {
                                        "$and": [{
                                            "$eq": [
                                                "$$metafield.key", "reviewCount"
                                            ]
                                        }, {
                                            "$eq": [
                                                "$$metafield.namespace",
                                                "vitals"
                                            ]
                                        }]
                                    }
                                }
                            }
                        },
                        "in": {
                            "$ifNull": [{
                                "$arrayElemAt": [
                                    "$$filteredMetafields.value", 0
                                ]
                            }, 0]
                        }
                    }
                },
                "feature_test": {
                    "$let": {
                        "vars": {
                            "filteredMetafields": {
                                "$filter": {
                                    "input": "$metafieldsDetails",
                                    "as": "metafield",
                                    "cond": {
                                        "$and": [{
                                            "$eq": [
                                                "$$metafield.key",
                                                "feature_test"
                                            ]
                                        }, {
                                            "$eq": [
                                                "$$metafield.namespace",
                                                "custom"
                                            ]
                                        }]
                                    }
                                }
                            }
                        },
                        "in": {
                            "$ifNull": [{
                                "$arrayElemAt": [
                                    "$$filteredMetafields.value", 0
                                ]
                            }, None]
                        }
                    }
                },
                "additional_notes_test": {
                    "$let": {
                        "vars": {
                            "filteredMetafields": {
                                "$filter": {
                                    "input": "$metafieldsDetails",
                                    "as": "metafield",
                                    "cond": {
                                        "$and": [{
                                            "$eq": [
                                                "$$metafield.key",
                                                "additional_notes_test"
                                            ]
                                        }, {
                                            "$eq": [
                                                "$$metafield.namespace",
                                                "custom"
                                            ]
                                        }]
                                    }
                                }
                            }
                        },
                        "in": {
                            "$ifNull": [{
                                "$arrayElemAt": [
                                    "$$filteredMetafields.value", 0
                                ]
                            }, None]
                        }
                    }
                },
                "specification_test": {
                    "$let": {
                        "vars": {
                            "filteredMetafields": {
                                "$filter": {
                                    "input": "$metafieldsDetails",
                                    "as": "metafield",
                                    "cond": {
                                        "$and": [{
                                            "$eq": [
                                                "$$metafield.key",
                                                "specification_test"
                                            ]
                                        }, {
                                            "$eq": [
                                                "$$metafield.namespace",
                                                "custom"
                                            ]
                                        }]
                                    }
                                }
                            }
                        },
                        "in": {
                            "$ifNull": [{
                                "$arrayElemAt": [
                                    "$$filteredMetafields.value", 0
                                ]
                            }, None]
                        }
                    }
                }
            }
        },
        {
            "$match": {
                "allVariantsUnavailable": False
            }
        },
        {
            "$group": {
                "_id": None,
                "filtered": {
                    "$push": "$$ROOT"
                },
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$project": {
                "filtered": {
                    "$cond": {
                        "if": {
                            "$gte": ["$count", 10]
                        },
                        "then": {
                            "$slice": ["$filtered", 10]
                        },
                        "else": "$filtered"
                    }
                }
            }
        },
        {
            "$unwind": "$filtered"
        },
        {
            "$replaceRoot": {
                "newRoot": "$filtered"
            }
        },
        {
            "$project": {
                "_id": 0,
                "description": 1,
                "featureImage": 1,
                "shopify_id": 1,
                "onlineStoreUrl": 1,
                "tags": 1,
                "title": 1,
                "productType": 1,
                "featuredImage": 1,
                "minPrice": "$priceRangeV2.minVariantPrice.amount",
                "maxPrice": "$priceRangeV2.maxVariantPrice.amount",
                "currencyCode": "$priceRangeV2.minVariantPrice.currencyCode",
                "handle": 1,
                "price": {
                    "$arrayElemAt": ["$variantDetails.price", 0]
                },
                "reviews": 1,
                "options": {
                    "$map": {
                        "input": "$optionsDetails",
                        "as": "option",
                        "in": {
                            "position": "$$option.position",
                            "name": "$$option.name",
                            "values": "$$option.values"
                        }
                    }
                },
                "images": {
                    "$reduce": {
                        "input": "$variantDetails",
                        "initialValue": [],
                        "in": {
                            "$concatArrays": ["$$value", ["$$this.image"]]
                        }
                    }
                },
    # "metafields": {
    #     "$map": {
    #         "input": "$metafieldsDetails",
    #         "as": "metafield",
    #         "in": {
    #             "namespace": "$$metafield.namespace",
    #             "key": "$$metafield.key",
    #             "value": "$$metafield.value"
    #         }
    #     }
    # },
                "variants": {
                    "$map": {
                        "input": "$variantDetails",
                        "as": "variant",
                        "in": {
                            "shopify_id": "$$variant.shopify_id",
                            "available": "$$variant.availableForSale",
                            "price": "$$variant.price",
                            "compareAtPrice": "$$variant.compareAtPrice",
                            "image": "$$variant.image",
                            "title": "$$variant.title"
                        }
                    }
                },
                "ratingValue": 1,
                "reviewCount": 1,
                "feature": "$feature_test",
                "additional_notes": "$additional_notes_test",
                "specification": "$specification_test"
            }
        }
    ]

    # 执行查询
    new_results = Product.objects.aggregate(query)

    # 假设 results 是从 MongoDB 查询得到的结果
    results_list.extend(list(new_results))    # 将 CommandCursor 对象转换为列表

    for i in range(len(results_list)):
        spec = results_list[i].get('specification', None)
        add_notes = results_list[i].get('additional_notes', None)
        feature = results_list[i].get('feature', None)

        if spec:
            data = json.loads(spec)

            # 准备转换后的字典
            result = {}

            # 解析 JSON 数据并填充字典
            current_key = None
            for item in data['children']:
                if item['type'] == 'paragraph':
                    current_key = item['children'][0]['value']
                    result[current_key] = []
                elif item['type'] == 'list':
                    for list_item in item['children']:
                        value = list_item['children'][0]['value']
                        result[current_key].append(value)
            results_list[i]['specification'] = result

        if add_notes:
            data = json.loads(add_notes)
            result = []

            # 解析 JSON 数据并填充字典

            for child in data['children']:
                if child['type'] == 'list':
                    for list_item in child['children']:
                        value = list_item['children'][0]['value']
                        result.append(value)

            results_list[i]['additional_notes'] = result

        if feature:
            data = json.loads(feature)
            result = []

            for child in data['children']:
                if child['type'] == 'list':
                    for list_item in child['children']:
                        value = list_item['children'][0]['value']
                        result.append(value)

            results_list[i]['feature'] = result

    # 成功返回
    return {
        'code': '0000',
        'data': {
            'result': results_list,
        },
        'msg': 'success'
    }, 200


# 根据用户的tags信息推荐礼物
def recommandGiftByTags(req):

    tags = req.get("tags")
    # 初始化 FlagModel
    emb_model = current_app.config['MODEL']

    if isinstance(tags, list):
        formatted_tags = ", ".join(tags)    # 将列表中的元素用逗号和空格分隔
    else:
        formatted_tags = tags    # 如果不是列表，假设它已经是一个字符串

    content = f"Based on the provided tags: {formatted_tags}, give me 10 gift recommendations that are closely related to these themes. "

    stream = g.clientOpenAI.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": content
        }],
        stream=True,
    )

    # match the user flow's branch
    typing_string_ = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            typing_string_ = typing_string_ + chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end='')

    # 初始化 FlagModel
    emb_model = current_app.config['MODEL']

    query_vector = emb_model.encode(typing_string_).astype(np.float64).tolist()
    # 构建聚合查询
    query = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "descriptionVector",
                "queryVector": query_vector,
    # "cosine": True,
                "numCandidates": 50,
                "limit": 20
            }
        },
        {
            "$match": {
                "status": "ACTIVE"
            }
        },
        {
            "$lookup": {
                "from":
                    "product_variant",    # The collection where the variants are stored.
                "localField":
                    "variants",    # The field in the products collection that holds the references.
                "foreignField":
                    "_id",    # The field in the variants collection that corresponds to the reference.
                "as":
                    "variantDetails"    # The field to populate with the results from the lookup.
            }
        },
        {
            "$addFields": {
                "similarityScore": {
                    "$meta": "vectorSearchScore"
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "description": 1,
                "featureImage": 1,
                "shopify_id": 1,
                "onlineStoreUrl": 1,
                "tags": 1,
                "title": 1,
                "productType": 1,
                "featuredImage": 1,
                "minPrice": "$priceRangeV2.minVariantPrice.amount",
                "maxPrice": "$priceRangeV2.maxVariantPrice.amount",
                "currencyCode": "$priceRangeV2.minVariantPrice.currencyCode",
                "handle": 1,
                "price": {
                    "$arrayElemAt": ["$variantDetails.price", 0]
                },
                "variants": {
                    "$map": {
                        "input": "$variantDetails",
                        "as": "variant",
                        "in": {
                            "shopify_id": "$$variant.shopify_id",
                            "available": "$$variant.availableForSale",
                            "price": "$$variant.price"
                        }
                    }
                }
            }
        }
    ]

    # 执行查询
    results = Product.objects.aggregate(query)

    # 假设 results 是从 MongoDB 查询得到的结果
    results_list = list(results)    # 将 CommandCursor 对象转换为列表

    # 成功返回
    return {
        'code': '0000',
        'data': {
            'result': results_list,
        },
        'msg': 'success'
    }, 200
