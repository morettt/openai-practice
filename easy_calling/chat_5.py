from openai import OpenAI

class AiSystem:

    def __init__(self):
        api_key = ''
        api_url = ''
        self.model = ''

        self.messages = [{'role': 'system', 'content': '你是一个可爱的AI'}]

        self.client = OpenAI(api_key=api_key, base_url=api_url)

    def add_message(self,role, content):

        self.messages.append({
            'role': role,
            'content': content
        })

    def get_requests(self):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )

        return response

    def ai_output(self,response):

        print('AI:', end='')
        full_content = ''

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                ai_content = chunk.choices[0].delta.content
                print(ai_content, end='', flush=True)

                full_content += ai_content

        print()

        return full_content

    def chat(self):
        user = input('你：')
        self.add_message('user', user)
        response = self.get_requests()
        ai_content = self.ai_output(response)
        self.add_message('assistant', ai_content)

    def main(self):
        while True:
            self.chat()

ai_system = AiSystem()
ai_system.main()




