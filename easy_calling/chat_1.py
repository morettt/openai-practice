from openai import OpenAI

api_key = ''
api_url = ''
model = ''

client = OpenAI(api_key=api_key,base_url=api_url)

response = client.chat.completions.create(
    model=model,
    messages=[{'role':'user','content':'你好啊！'}]
)

ai_content = response.choices[0].message.content

print(f'AI:{ai_content}')


