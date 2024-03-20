from flask import g, current_app
from FlagEmbedding import FlagModel
import numpy as np


def gift_recommendation(req, res):

    # get the user's input
    genders, occasions, budgets, ages, interests, relationships, styles = req

    user_Need_List = {
        "genders": genders,
        "occasions": occasions,
        "budgets": budgets,
        "ages": ages,
        "interests": interests,
        "relationships": relationships,
        "styles": styles
    }

    #
    content = f"A product suitable for {user_Need_List['ages']} individuals, who are interested in {user_Need_List['interests']} and looking for something for {user_Need_List['occasions']}. Considering the budget is {user_Need_List['budgets']}, and it's meant for {user_Need_List['relationships']} relationships. The preferred style is {user_Need_List['styles']}. How would you describe such a product? Please provide a description that captures the essence of these criteria."

    # 初始化 FlagModel, TODO: I don't think the chinese model may be suitable for English products.
    emb_model = FlagModel('./Models/BAAI/bge-large-zh-v1.5',
                          query_instruction_for_retrieval="为这个句子生成表示以用于检索商品：",
                          use_fp16=True)

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

    # encode the project string
    query_vector = emb_model.encode(project_string_).astype(np.float64).tolist()

    # 假设 user_Need_List['budgets'] 是从之前的 budgets 数组中选出的一个值
    budget = user_Need_List['budgets']

    if budget == 'Under $50':
        price_min = 0
        price_max = 50

    elif budget == '$50-$100':
        price_min = 50
        price_max = 100

    elif budget == '$100-$200':
        price_min = 100
        price_max = 200

    elif budget == 'Above $200':
        price_min = 200
        # 为 price_max 设置一个高值，或者可以根据应用场景决定是否需要上限
        price_max = 1000000    # 假设作为一个高的上限值

    print(f"Price range: {price_min} to {price_max}")

    # 构建聚合查询
    query = [{
        "$vectorSearch": {
            "index": "vector_index",
            "path": "Description Vector",
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

    return
