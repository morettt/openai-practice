from openai import OpenAI

api_key = ''
api_url = ''
model = ''

messages = [{'role':'system','content':'你是一个可爱的AI'}]


client = OpenAI(api_key=api_key,base_url=api_url)

def add_message(role,content):

    messages.append({
        'role':role,
        'content':content
    })

def get_requests():

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    return response

def ai_output(response):

    print('AI:',end='')
    full_content = ''

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            ai_content = chunk.choices[0].delta.content
            print(ai_content,end='',flush=True)

            full_content+=ai_content

    print()

    return full_content


def chat():
    user = input('你：')
    add_message('user',user)
    response = get_requests()
    ai_content = ai_output(response)
    add_message('assistant',ai_content)

def main():
    while True:
        chat()

if __name__ == '__main__':
    main()


