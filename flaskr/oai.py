from openai import OpenAI
from flask import current_app, g


# connect with openai service
def get_openai_service():

    if 'clientOpenAI' not in g:
        g.clientOpenAI = OpenAI(api_key=current_app.config['OPENAI_KEY'])

    return g.clientOpenAI


# disconnect with openai service
def close_openai_service(e=None):
    oai = g.pop('clientOpenAI', None)


def write_by_ai(input: str) -> str:
    ''' 
    This function accept the customer's input and return a suitable greeting card message
    '''
    clientOpenAI = get_openai_service()

    if not input:
        return f"This is the gift I bought for you."

    prompt = f'Rewrite the input sentence as a greeting card messages. Do not include any information that the input not includes. ### Input:{input}\n### Output:'

    # 调用GPT接口
    response = clientOpenAI.chat.completions.create(
        model="gpt-3.5-turbo",
        presence_penalty=1.1,
        max_tokens=150,
        temperature=0.8,    # 增加随机性，同样输入每次生成内容会不一样
        messages=[{
            "role":
                "system",
            "content":
                f"You are a writer who specializes in rewriting sentence to greeting card messages. Keep mind using an appropriate tone for the recipient."
        }, {
            "role": "user",
            "content": prompt
        }])
    res = response.choices[0].message.content
    return {
        'code': "0000",
        'message': "Success",
        'data': res.replace('"', "")
    }, 200
