from flask import g, current_app, jsonify
from FlagEmbedding import FlagModel
import numpy as np
import re
from FlagEmbedding import FlagModel
import os
from pymilvus import MilvusClient, DataType
import json
from openai import OpenAI
import time


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

    opi_client = OpenAI(api_key=current_app.config['OPENAI_KEY'])
    stream = opi_client.chat.completions.create(
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
    os.path.join(os.path.dirname(__file__), 'models/bge-large-zh-v1.5')
    # 初始化 FlagModel

    start_time = time.time()

    emb_model = FlagModel(os.path.join(
        os.path.dirname(__file__),
        'models/models--BAAI--bge-large-zh-v1.5/snapshots/c11661ba3f9407eeb473765838eb4437e0f015c0'
    ),
                          query_instruction_for_retrieval="为这个句子生成表示以用于检索商品：",
                          use_fp16=True)

    query_vector = emb_model.encode(user_typing).astype(np.float64).tolist()

    end_time = time.time()
    print(
        f"Time taken to load the model and encode the user's input: {end_time - start_time} seconds"
    )

    # 构建聚合查询
    # query = [{
    #     "$vectorSearch": {
    #         "index": "vector_index",
    #         "path": "description_vector",
    #         "queryVector": query_vector,
    #         "numCandidates": 50,
    #         "limit": 10,
    #     }
    # }, {
    #     "$addFields": {
    #         "similarityScore": {
    #             "$meta": "vectorSearchScore"
    #         }
    #     }
    # }]

    # 执行查询
    # results = g.db.test2.products.aggregate(query)
    # 假设 results 是从 MongoDB 查询得到的结果
    # results_list = list(results)    # 将 CommandCursor 对象转换为列表

    # 提取前三个结果的id，top_three_ids用来记录出现过的商品，不重复推荐
    # top_three_ids = [result['id'] for result in results_list[:3]]
    # print(top_three_ids)

    # for i in range(len(results_list)):
    #     if 'description_vector' in results_list[i].keys():
    #         del results_list[i]['description_vector']
    #     if '_id' in results_list[i].keys():
    #         del results_list[i]['_id']

    start_time = time.time()

    client = MilvusClient(uri=current_app.config['CLUSTER_ENDPOINT'],
                          token=current_app.config['TOKEN'])

    # Single vector search
    res = client.search(
        collection_name="products",
        data=[query_vector],
        limit=10,    # Max. number of search results to return
        search_params={
            "metric_type": "COSINE",
            "params": {}
        }    # Search parameters
    )

    end_time = time.time()
    print(f"time taken to search: {end_time - start_time} seconds")

    start_time = time.time()
    # Convert the output to a formatted JSON string
    result_json = json.dumps(res, indent=4)
    print(result_json)
    result_json = json.loads(result_json)

    end_time = time.time()
    print(f"time taken to format the result: {end_time - start_time} seconds")

    # 打印结果
    # for result in result_json:
    #     # print(result.keys())

    #     print(
    #         f"ID: {result_json['id']}, Similarity Score: {result_json['distance']}"
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
            'result': result_json,
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
    emb_model = FlagModel(os.path.join(
        os.path.dirname(__file__),
        'models/models--BAAI--bge-large-zh-v1.5/snapshots/c11661ba3f9407eeb473765838eb4437e0f015c0'
    ),
                          query_instruction_for_retrieval="为这个句子生成表示以用于检索商品：",
                          use_fp16=True)

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

    opi_client = OpenAI(api_key=current_app.config['OPENAI_KEY'])
    stream = opi_client.chat.completions.create(
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
