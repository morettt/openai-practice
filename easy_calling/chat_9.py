from openai import OpenAI
import base64
from PIL import ImageGrab
import io

API_KEY = ''
API_URL = ''
messages = [
    {'role': 'system', 'content': '你是一个聪明可爱的AI'}
]

client = OpenAI(api_key=API_KEY, base_url=API_URL)

def get_image_base64():

    screensho = ImageGrab.grab()
    buffer = io.BytesIO()
    screensho.save(buffer,format='JPEG')
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    print('截图！！！')
    return image_data

def add_message(role,content):
    messages.append({
        'role':role,
        'content':content
    })



def add_vl_message(content,image_data):
    messages.append({
        'role':'user',
        'content':[
            {'type':'text','text':content},
            {'type':'image_url','image_url':{'url':f'data:image/jpeg;base64,{image_data}'}}
        ]
    })


def get_response():

    response = client.chat.completions.create(
        model='gemini-2.0-flash',
        messages=messages,
        stream=True
    )

    return response

def handle_response(response):

    full_assistant = ''
    print('AI',end='')

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            ai_response = chunk.choices[0].delta.content
            print(ai_response,end='',flush=True)

            full_assistant+=ai_response
    print()
    return full_assistant

def start_chat():
    while True:
        user = input('你：')

        imade_data = get_image_base64()

        add_vl_message(user, imade_data)
        response = get_response()
        ai_response = handle_response(response)
        add_message('assistant', ai_response)

if __name__ == '__main__':
    start_chat()