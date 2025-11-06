from openai import OpenAI
import json
import inspect
from tools import TOOL_FUNCTIONS


API_KEY = 'sk-zk2cb9d4e3ac5605d1c54de9a747348c71868ccc8e0a29b4'
API_URL = 'https://api.zhizengzeng.com/v1'
messages = [
    {'role': 'system', 'content': '你是一个耐心温柔的AI，你很可爱,不喜欢喋喋不休的说话，讨厌说一堆的话,不会1、2、3、4这样说话，是一个猫娘'}
]
window_size = 10

client = OpenAI(api_key=API_KEY, base_url=API_URL)


def create_tools():
    """动态创建工具配置"""
    tools = []

    for name, func in TOOL_FUNCTIONS.items():
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

    return tools


tools = create_tools()


def get_requests():
    response = client.chat.completions.create(
        model='gemini-2.0-flash',
        messages=messages,
        stream=False,
        tools=tools
    )
    return response


def accept_chat(response):
    message = response.choices[0].message

    if message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": message.tool_calls
        })

        # 处理所有工具调用
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            print(f'AI想要调用：{function_name}')

            if tool_call.function.arguments:
                arg = json.loads(tool_call.function.arguments)
                print(f'参数：{arg}')
                result = TOOL_FUNCTIONS[function_name](**arg)
            else:
                result = TOOL_FUNCTIONS[function_name]()

            print(f'结果：{result}')

            messages.append({
                'role': 'tool',
                'content': f'结果：{result}',
                'tool_call_id': tool_call.id,
                'name': function_name
            })

        ai_response = get_requests()
        ai_content = ai_response.choices[0].message.content
        print(f'AI:{ai_content}')
        return ai_content

    content = message.content
    print(f'AI:{content}')
    return content


def add_message(role, content):
    messages.append({
        'role': role,
        'content': content
    })

    if len(messages) > window_size:
        messages.pop(1)


def chat():
    print(messages)
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
