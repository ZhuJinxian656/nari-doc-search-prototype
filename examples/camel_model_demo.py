# src/main.py

import os
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.typing import ModelType, TaskType

# 1. 从 .env 文件加载环境变量
# 确保这行代码在所有其他 CAMEL 导入和使用之前
load_dotenv()

def main():
    """
    主函数，用于设置和运行 CAMEL AI Agent 协作任务。
    """
    print("欢迎来到 CAMEL AI 协作世界！")
    print("-" * 30)
    
    # 2. 定义任务和角色
    # 我们让一个科幻小说家和一个物理学家，共同构思一个关于“时间旅行”的短篇故事大纲。
    task_prompt = "构思一个关于时间旅行的短篇故事大纲，要求既有创意，又符合基本的物理学原理。"
    
    # 获取模型名称，如果环境变量没有设置，则使用默认值
    # 这里我们从 .env 文件中加载了，所以会使用 "Qwen2-72B-Instruct"
    model_name = os.getenv("OPENAI_API_MODEL")
    if not model_name:
        raise ValueError("环境变量 OPENAI_API_MODEL 未设置，请检查你的 .env 文件。")
        
    print(f"使用的模型: {model_name}")
    print(f"任务: {task_prompt}")
    print("-" * 30)

    # 3. 创建 Agent
    # AI 助手 Agent (扮演科幻小说家)
    assistant_sys_msg = BaseMessage.make_assistant_message(
        role_name="科幻小说家",
        content="我擅长创作富有想象力的科幻故事，特别是关于未来科技和时空穿梭的情节。",
    )
    assistant_agent = ChatAgent(
        system_message=assistant_sys_msg,
        model=ModelType.OPENAI, # 注意：即使是本地模型，只要接口兼容，这里就用 ModelType.OPENAI
        model_config=dict(model=model_name), # 明确指定模型名称
        task_prompt=task_prompt, # 让 Agent 知道总体任务
    )

    # AI 用户 Agent (扮演物理学家)
    user_sys_msg = BaseMessage.make_user_message(
        role_name="物理学家",
        content="我专注于理论物理，特别是相对论和量子力学。我会确保故事中的科学概念是严谨和合理的。",
    )
    user_agent = ChatAgent(
        system_message=user_sys_msg,
        model=ModelType.OPENAI,
        model_config=dict(model=model_name),
        task_prompt=task_prompt,
    )
    
    # 4. 重置 Agent，准备开始对话
    assistant_agent.reset()
    user_agent.reset()

    # 5. 开始多轮对话 (Role-Playing)
    # 助手先开始，提出初步想法
    assistant_msg = assistant_agent.step(user_agent.system_message)
    print(f"【{assistant_agent.role_name}】: {assistant_msg.content}\n")

    # 限制对话轮次，避免无限循环
    for _ in range(5): # 进行5轮对话
        # 用户（物理学家）根据助手的想法进行回应和修正
        user_msg = user_agent.step(assistant_msg)
        print(f"【{user_agent.role_name}】: {user_msg.content}\n")
        
        # 助手（小说家）再根据用户的反馈进行创作
        assistant_msg = assistant_agent.step(user_msg)
        print(f"【{assistant_agent.role_name}】: {assistant_msg.content}\n")

    print("-" * 30)
    print("任务完成！")

if __name__ == "__main__":
    main()