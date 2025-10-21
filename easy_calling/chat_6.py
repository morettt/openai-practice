from openai import OpenAI
import json


class AiSystem:

    def __init__(self):
        # 基本API的配置
        # 注意：实际应用中，api_key和base_url应通过环境变量等方式安全加载
        api_key = 'sk-zk231afdd49ac82b15607ce790bb887264a68d1b3698612a'
        api_url = 'https://api.zhizengzeng.com/v1'
        self.model = 'gemini-2.0-flash'

        # 记录对话历史，系统消息通常是第一条
        self.messages = [{'role': 'system', 'content': '你是一个可爱的AI，是一个傲娇可爱的喵娘'}]

        # 1. 🌟 新增：对话轮数阈值和计数器
        # 这里一轮对话指 (用户输入 + AI回复) = 2 条 message
        self.compression_threshold = 10  # 例如：超过 10 条消息 (5轮对话) 就触发总结
        # 排除系统消息，所以从 0 开始
        self.current_message_count = 0

        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=api_key, base_url=api_url)

    def add_message(self, role, content):
        # 角色、内容相关的
        self.messages.append({
            'role': role,
            'content': content
        })
        # 每新增一条消息，计数器 +1
        self.current_message_count += 1

    def get_requests(self):
        # ... (与原版相同)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        return response

    def ai_output(self, response):
        # ... (与原版相同)
        print('AI:', end='')
        full_content = ''
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                ai_content = chunk.choices[0].delta.content
                print(ai_content, end='', flush=True)
                full_content += ai_content
        print()
        return full_content

    # 2. 🌟 新增：总结压缩功能
    def _check_and_compress_history(self):
        # 如果当前消息数量（不含系统消息）超过阈值，则进行压缩
        if self.current_message_count > self.compression_threshold:
            print("\n--- 📝 触发历史对话总结和压缩... ---")

            # 1. 提取需要总结的历史对话 (除了系统消息)
            history_to_summarize = self.messages[1:]

            # 2. 构造总结用的 prompt
            summary_prompt = "请根据以下历史对话，用简洁的语言总结出一个**精炼的、连贯的**摘要，摘要应以'我们进行了以下对话：'开头，重点保留对话的主题、关键信息和尚未解决的问题，以便AI基于这个摘要继续对话。请直接输出摘要内容，不要添加任何其他解释或评论。\n\n"
            summary_prompt += json.dumps(history_to_summarize, ensure_ascii=False, indent=2)

            # 3. 调用模型进行总结 (使用一个轻量级模型即可)
            try:
                summary_response = self.client.chat.completions.create(
                    model='gemini-2.5-flash',  # 可以使用更便宜的模型进行总结
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ],
                    temperature=0.0  # 确保总结内容稳定
                )
                summary_content = summary_response.choices[0].message.content
                print(f"--- 摘要完成，长度：{len(summary_content)} 字符 ---")

                # 4. 替换历史消息
                system_message = self.messages[0]
                # 新的摘要消息，作为 system message 之外的**第二条**消息
                summary_message = {'role': 'system', 'content': summary_content}

                # 保留系统消息 + 摘要消息 + **最后两条** (用户最新输入和AI最新回复，防止马上忘记)
                # 假设 chat() 中已经 add 了 user/assistant 消息，它们就是最后两条
                last_two_messages = self.messages[-2:]

                self.messages = [system_message, summary_message] + last_two_messages

                # 5. 重置计数器
                # 现在的消息数量：系统消息(1) + 摘要消息(1) + 最后两条(2) = 4
                self.current_message_count = 2  # 仅计算 user/assistant 消息

            except Exception as e:
                print(f"\n--- ❌ 总结过程中出错，跳过压缩：{e} ---")

    def chat(self):
        # 1. 检查并压缩历史（在用户提问前执行）
        self._check_and_compress_history()
        print(self.messages)

        # 2. 用户输入和新增 user 消息
        user = input('你：')
        self.add_message('user', user)

        # 3. 获取 AI 回复
        response = self.get_requests()
        ai_content = self.ai_output(response)

        # 4. 新增 assistant 消息
        self.add_message('assistant', ai_content)

        print(f"(当前消息总数（不含系统/摘要）：{self.current_message_count})")

    def main(self):
        while True:
            self.chat()

ai_system = AiSystem()
ai_system.main()