from openai import OpenAI
import json
import threading


class AiSystem:

    def __init__(self):
        # 基本API的配置
        api_key = 'sk-zk231afdd49ac82b15607ce790bb887264a68d1b3698612a'
        api_url = 'https://api.zhizengzeng.com/v1'
        self.model = 'gemini-2.0-flash'

        # 记录对话历史
        self.messages = [{'role': 'system', 'content': '你是一个可爱的AI，是一个傲娇可爱的喵娘'}]

        # 对话轮数阈值和计数器
        self.compression_threshold = 10  # 超过10条消息就触发总结
        self.current_message_count = 0

        # 🌟 异步压缩相关
        self.is_compressing = False  # 是否正在压缩
        self.compression_lock = threading.Lock()  # 线程锁

        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=api_key, base_url=api_url)

    def add_message(self, role, content):
        self.messages.append({
            'role': role,
            'content': content
        })
        # 每新增一条消息，计数器 +1
        self.current_message_count += 1

    def get_requests(self):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        return response

    def ai_output(self, response):
        print('AI:', end='')
        full_content = ''
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                ai_content = chunk.choices[0].delta.content
                print(ai_content, end='', flush=True)
                full_content += ai_content
        print()
        return full_content

    def _async_compress_history(self):
        """🌟 后台异步执行压缩"""
        # 检查是否已经在压缩
        with self.compression_lock:
            if self.is_compressing:
                return  # 如果已经在压缩，跳过
            self.is_compressing = True
            print("\n--- 🔄 后台开始总结历史对话（不影响继续聊天）... ---")

        try:
            # 1. 快照当前需要总结的消息（避免被新对话干扰）
            # 获取所有 user/assistant 消息
            with self.compression_lock:
                all_conversations = [m for m in self.messages if m['role'] in ['user', 'assistant']]

                # 如果消息不够多，不压缩
                if len(all_conversations) <= 4:
                    self.is_compressing = False
                    return

                # 保留最后4条（2轮对话），其余的用来总结
                messages_to_summarize = all_conversations[:-4]
                history_snapshot = messages_to_summarize.copy()

            # 2. 构造总结 prompt
            summary_prompt = "请根据以下历史对话，用简洁的语言总结出一个**精炼的、连贯的**摘要，摘要应以'我们之前进行了以下对话：'开头，重点保留对话的主题、关键信息和尚未解决的问题，以便AI基于这个摘要继续对话。请直接输出摘要内容，不要添加任何其他解释或评论。\n\n"
            summary_prompt += json.dumps(history_snapshot, ensure_ascii=False, indent=2)

            # 3. 调用模型进行总结（这部分耗时，但不阻塞主线程）
            summary_response = self.client.chat.completions.create(
                model='gemini-2.0-flash',  # 使用快速模型进行总结
                messages=[
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.0  # 确保总结内容稳定
            )
            summary_content = summary_response.choices[0].message.content

            # 4. 压缩完成后，替换历史
            with self.compression_lock:
                system_message = self.messages[0]
                # 🌟 改成 assistant 角色
                summary_message = {'role': 'assistant', 'content': f"[历史对话摘要]\n{summary_content}"}

                # 获取最新的对话消息（可能在压缩过程中又增加了新对话）
                current_conversations = [m for m in self.messages if m['role'] in ['user', 'assistant']]
                recent_messages = current_conversations[-4:]  # 保留最后4条

                # 重建消息列表
                self.messages = [system_message, summary_message] + recent_messages

                # 重置计数器（只计算 user/assistant 消息）
                self.current_message_count = len(recent_messages)

                print(f"\n--- ✅ 历史压缩完成！总结了 {len(history_snapshot)} 条消息 → 1 条摘要 ---")
                print(f"--- 当前保留：系统消息(1) + 摘要(1) + 最近对话({len(recent_messages)}) ---\n")
                self.is_compressing = False

        except Exception as e:
            print(f"\n--- ❌ 压缩过程中出错：{e} ---\n")
            with self.compression_lock:
                self.is_compressing = False

    def chat(self):
        print(self.messages)
        # 1. 用户输入
        user = input('你：')
        self.add_message('user', user)

        # 2. 获取 AI 回复
        response = self.get_requests()
        ai_content = self.ai_output(response)

        # 3. 新增 assistant 消息
        self.add_message('assistant', ai_content)

        # 4. 🌟 检查是否需要压缩（异步触发，不阻塞）
        if self.current_message_count > self.compression_threshold and not self.is_compressing:
            # 在后台线程中执行压缩，不阻塞对话
            compress_thread = threading.Thread(
                target=self._async_compress_history,
                daemon=True  # 守护线程，主程序退出时自动结束
            )
            compress_thread.start()

        # 显示当前状态
        status = f"正在压缩中..." if self.is_compressing else ""
        print(f"(当前消息数：{self.current_message_count}) {status}")

    def main(self):
        print("=== 😺 喵娘AI聊天系统（支持异步历史压缩）===")
        print(f"提示：超过 {self.compression_threshold} 条消息后会自动在后台压缩历史\n")

        while True:
            self.chat()


if __name__ == "__main__":
    ai_system = AiSystem()
    ai_system.main()