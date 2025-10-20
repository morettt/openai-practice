from openai import OpenAI

api_key = ''
api_url = ''
model = ''

client = OpenAI(api_key=api_key,base_url=api_url)

response = client.chat.completions.create(
    model=model,
    messages=[{'role':'user','content':'讲一个故事！'}],
    stream=True
)

print('AI:',end='')

for chunk in response:
    if chunk.choices[0] and chunk.choices[0].delta.content is not None:
        ai_content = chunk.choices[0].delta.content
        print(ai_content,end='',flush=True)




