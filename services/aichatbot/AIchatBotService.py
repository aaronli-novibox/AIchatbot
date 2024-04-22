from flask import g, current_app, jsonify
from FlagEmbedding import FlagModel
import numpy as np
import re
from FlagEmbedding import FlagModel
import os
import shopify
from pathlib import Path
import json


def flatten_data(data):
    """
    递归地移除'data'、'node'和'nodes'键，返回处理后的数据。
    """
    if isinstance(data, dict):
        if "data" in data:
            return flatten_data(data["data"])
        elif "node" in data:
            return flatten_data(data["node"])
        elif "products" in data:
            return flatten_data(data["products"])
        elif "nodes" in data:
            return [flatten_data(item) for item in data["nodes"]]

        else:
            return {
                k: flatten_data(v)
                for k, v in data.items()
                if data.get('onlineStoreUrl') is not None
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

    if_succ = True

    if branch_index == 1:
        print("branch 1")
        return recommandGiftByUserInput(req)

    elif branch_index == 2:

        print("branch 2")
        # 这里跳转到历史订单查询的代码
        return jsonify({
            'code':
                '0002',
            'data': {
                'result': None,
            },
            'msg':
                'The user wants to query historical order information, logistics information, etc. 请求查询历史订单信息等'
        })

    elif branch_index == 3:

        print("branch 3")
        # 这里跳转到闲聊的代码
        return jsonify({
            'code': '0003',
            'data': {
                'result': None,
            },
            'msg': 'The user is using our conversation for casual chat. 请求闲聊'
        })

    elif branch_index == 4:

        print("branch 4")
        # 这里跳转到提示用户输入的代码
        return jsonify({
            'code': '0004',
            'data': {
                'result': None,
            },
            'msg': 'Unable to identify user intent. 搞不懂用户请求'
        })


# 根据用户的聊天框输入推荐礼物
def recommandGiftByUserInput(req):

    user_typing = req["user_typing"]

    content = f'''Here is a user's input:"{user_typing}", give me a list of 5 terms to describe the potential product. You must include the products mentioned in the input. The output must be a json'''
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

    os.path.join(os.path.dirname(__file__), 'models/bge-large-zh-v1.5')
    # 初始化 FlagModel
    emb_model = current_app.config['MODEL']

    query_vector = emb_model.encode(typing_string_).astype(np.float64).tolist()

    # 构建聚合查询
    query = [{
        "$vectorSearch": {
            "index": "vector_index",
            "path": "description_vector",
            "queryVector": query_vector,
            "numCandidates": 50,
            "limit": 10,
        }
    }, {
        "$addFields": {
            "similarityScore": {
                "$meta": "vectorSearchScore"
            }
        }
    }]

    # 执行查询
    results = g.db.test2.products.aggregate(query)
    # 假设 results 是从 MongoDB 查询得到的结果
    results_list = list(results)    # 将 CommandCursor 对象转换为列表

    # 提取前三个结果的id，top_three_ids用来记录出现过的商品，不重复推荐
    # top_three_ids = [result['id'] for result in results_list[:3]]
    # print(top_three_ids)

    # 连接shopify
    shop_url = f"{current_app.config['SHOPIFY_SHOP_NAME']}.myshopify.com"
    api_version = '2024-01'
    private_app_password = current_app.config['SHOPIFY_API_PASSWORD']
    session = shopify.Session(shop_url, api_version, private_app_password)
    shopify.ShopifyResource.activate_session(session)

    ids = []

    for i in range(len(results_list)):
        if 'description_vector' in results_list[i].keys():
            del results_list[i]['description_vector']
        if '_id' in results_list[i].keys():
            del results_list[i]['_id']
        ids.append(results_list[i]['id'])

    print(ids)
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    document = Path(os.path.join(script_dir,
                                 "laohuji_query.graphql")).read_text()

    productInfo = shopify.GraphQL().execute(query=document,
                                            variables={"product_ids": ids},
                                            operation_name="GetManyProducts")

    productInfo = json.loads(productInfo)
    productInfo = flatten_data(productInfo)

    # 打印结果
    # for result in results_list[0:3]:
    #     print(result.keys())

    #     print(
    #         f"ID: {result['id']}, Similarity Score: {result['similarityScore']}"
    #     )
    #     if result['similarityScore'] <= 0.35:
    #         if_succ = False
    #         print("这里跳转到提示让他们填表单找礼物的功能")
    #         return jsonify({
    #             'code':
    #                 '0001',
    #             'data': {
    #                 'result': None,
    #             },
    #             'msg':
    #                 'The user\'s input is a description of the goods they need to purchase, but similarity score is too low. 请求推荐礼物, 但是礼物推荐的相似度太低, 推荐失败'
    #         })

    # 成功返回
    return jsonify({
        'code':
            '0000',
        'data': {
    # 'result': results_list[0:3],
            'result': productInfo,
        },
        'msg':
            'The user\'s input is a description of the goods they need to purchase, and recommand success. 请求推荐礼物, 推荐成功'
    })


# 根据用户提供的信息推荐礼物
def recommandGiftByList(req):

    # get the user's input: relationship, interests, style are optional, if not provided, use default values
    gender = req.get("gender")
    occasion = req.get("occasion")
    budget = req.get("budget")
    age = req.get("age")
    relationship = req.get("relationship", None)    # 如果不存在，则返回 None
    interests = req.get("interests", None)    # 如果不存在，则返回 None
    style = req.get("style", None)    # 如果不存在，则返回 None

    # 初始化 FlagModel
    emb_model = current_app.config['MODEL']

    # 构建内容的各个部分
    parts = [f"A product suitable for {age} {gender} individuals"]

    if interests is not None:
        parts.append(f", who are interested in {interests}")

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

    print(content)

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
    if budget == "Under $50":
        price_min = 0
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
    query = [{
        "$vectorSearch": {
            "index": "vector_index",
            "path": "description_vector",
            "queryVector": query_vector,
            "numCandidates": 50,
            "limit": 10
        }
    }, {
        "$match": {
            "Price": {
                "$gte": price_min,
                "$lte": price_max
            }
        }
    }]

    # 执行查询
    results = g.db.test2.products.aggregate(query)

    # 假设 results 是从 MongoDB 查询得到的结果
    results_list = list(results)    # 将 CommandCursor 对象转换为列表

    # # 提取前三个结果的id，top_three_ids用来记录出现过的商品，不重复推荐
    # top_three_ids = [result['id'] for result in results_list[:3]]
    # print(top_three_ids)

    # 打印结果
    print(results_list[0:3])

    # 成功返回
    return jsonify({
        'code': '0000',
        'data': {
    # 'result': results_list[0:3],
            'result': results_list,
        },
        'msg': 'success'
    })
