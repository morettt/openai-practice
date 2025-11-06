from openai import OpenAI
from datetime import datetime
import json
import inspect
import requests

API_KEY = ''
API_URL = ''
model = ''
messages = [
    {'role': 'system', 'content': '你是一个傲娇的AI'}
]

client = OpenAI(api_key=API_KEY, base_url=API_URL)

# 定义工具函数
def get_current_time():
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_acg_pic(device="wap"):
    """
    获取随机ACG图片
    device: "pc" 或 "wap"
    """
    url = f"https://v2.xxapi.cn/api/randomAcgPic?type={device}"
    try:
        response = requests.get(url).json()
        return response['data']
    except Exception as e:
        return f"获取图片失败: {str(e)}"


FUNCTIONS = {
    'get_current_time': get_current_time,
    'get_acg_pic': get_acg_pic
}

tools = []

for name, func in FUNCTIONS.items():
    sig = inspect.signature(func)

    properties = {} 
    required = []

    for param_name, param in sig.parameters.items():
        properties[param_name] = {
            "type": "string",
            "description": param_name
        }

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    tool = {
        "type": "function",
        "function": {
            "name": name,
            "description": func.__doc__ or "无描述",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }
    tools.append(tool)


def get_requests():
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools
    )
    return response

def accept_chat(response):
    message = response.choices[0].message

    if message.tool_calls:

        messages.append({
            "role":"assistant",
            "content":message.content,
            "toll_calls":message.tool_calls
        })

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name

            print(f'ai想要用：{function_name}')

            if tool_call.function.arguments:
                argus = json.loads(tool_call.function.arguments)
                print(f'参数：{argus}')
                result = FUNCTIONS[function_name](**argus)

            else:
                result = FUNCTIONS[function_name]()
            print(f'结果：{result}')


            messages.append({
                "role":"tool",
                "content":f'结果：{result}',
                "tool_call_id":tool_call.id,
                "name":name
            })

            ai_response = get_requests()
            ai_tool_content = ai_response.choices[0].message.content
            print(f'ai:{ai_tool_contentt}')
            return ai_tool_content

    content = message.content
    print(f'AI：{content}')
    return content

    content = message.content
    print(f'AI:{content}')
    return content

def add_message(role, content):
    messages.append({
        'role': role,
        'content': content
    })


def chat():
    user = input('你：')
    add_message('user', user)
    response = get_requests()
    ai_content = accept_chat(response)
    add_message('assistant', ai_content)

def main():
    while True:
        chat()

if __name__ == '__main__':
    main()
