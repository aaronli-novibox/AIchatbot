from flask import g, current_app, jsonify
from FlagEmbedding import FlagModel
import numpy as np
import re
import os
import shopify
from pathlib import Path
import json
import time
from flaskr.product_mongo import *


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
    content = f"You need to help me determine the next branch direction based on the user's freely entered content. We have the following branch directions: 1. The user's input is a description of the goods they need to purchase, and we will make recommendations based on the user's input next. 2. The user wants to query historical order information, logistics information, etc. 3. The user is using our conversation for casual chat. 4. Unable to identify user intent. The following is the user's conversation {user_typing}. Please determine the branch. If it is branch 1, reply with 1, and so on."

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

    branch_index = matchBranch(typing_string_)

    if branch_index == 1:

        return recommandGiftByUserInput(req)

    elif branch_index == 2:

        # 这里跳转到历史订单查询的代码
        return {
            'code':
                '0002',    # '0002'代表请求查询历史订单信息等
            'data': {
                'result': None,
            },
            'msg':
                'The user wants to query historical order information, logistics information, etc. 请求查询历史订单信息等'
        }, 200

    elif branch_index == 3:

        # 这里跳转到闲聊的代码
        return {
            'code': '0003',    # '0003'代表用户在使用我们的对话进行闲聊
            'data': {
                'result': None,
            },
            'msg': 'The user is using our conversation for casual chat. 请求闲聊'
        }, 200

    elif branch_index == 4:

        # 这里跳转到提示用户输入的代码
        return {
            'code': '0004',    # '0004'代表无法识别用户意图
            'data': {
                'result': None,
            },
            'msg': 'Unable to identify user intent. 搞不懂用户请求'
        }, 200


# 根据用户的聊天框输入推荐礼物
def recommandGiftByUserInput(req):

    user_typing = req["user_typing"]

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
    # "cosine": True,
                "numCandidates": 50,
                "limit": 10
            }
        },
        {
            "$match": {
                "status": "ACTIVE"    # 先筛选状态为ACTIVE的文档
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
                "priceRangeV2": 1,
                "tags": 1,
                "title": 1,
                "productType": 1,
                "featuredImage": 1,
            }
        }
    ]

    # 执行查询
    # results = g.db.dev.product.aggregate(query)
    results = Product.objects.aggregate(query)
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

    stream = g.clientOpenAI.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": content
        }],
        stream=True,
    )
    project_string_ = ""
    print("I guess you need the commodity that\n")
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            project_string_ = project_string_ + chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end='')

    query_vector = emb_model.encode(project_string_).astype(np.float64).tolist()

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

    # 构建聚合查询
    query = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "descriptionVector",
                "queryVector": query_vector,
    # "cosine": True,
                "numCandidates": 50,
                "limit": 10
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
