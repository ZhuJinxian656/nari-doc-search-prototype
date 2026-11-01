# src/main.py

import os
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.typing import ModelType, TaskType

# 1. �� .env �ļ����ػ�������
# ȷ�����д������������� CAMEL �����ʹ��֮ǰ
load_dotenv()

def main():
    """
    ���������������ú����� CAMEL AI Agent Э������
    """
    print("��ӭ���� CAMEL AI Э�����磡")
    print("-" * 30)
    
    # 2. ��������ͽ�ɫ
    # ������һ���ƻ�С˵�Һ�һ������ѧ�ң���ͬ��˼һ�����ڡ�ʱ�����С��Ķ�ƪ���´�١�
    task_prompt = "��˼һ������ʱ�����еĶ�ƪ���´�٣�Ҫ����д��⣬�ַ��ϻ���������ѧԭ����"
    
    # ��ȡģ�����ƣ������������û�����ã���ʹ��Ĭ��ֵ
    # �������Ǵ� .env �ļ��м����ˣ����Ի�ʹ�� "Qwen2-72B-Instruct"
    model_name = os.getenv("OPENAI_API_MODEL")
    if not model_name:
        raise ValueError("�������� OPENAI_API_MODEL δ���ã�������� .env �ļ���")
        
    print(f"ʹ�õ�ģ��: {model_name}")
    print(f"����: {task_prompt}")
    print("-" * 30)

    # 3. ���� Agent
    # AI ���� Agent (���ݿƻ�С˵��)
    assistant_sys_msg = BaseMessage.make_assistant_message(
        role_name="�ƻ�С˵��",
        content="���ó����������������Ŀƻù��£��ر��ǹ���δ���Ƽ���ʱ�մ������ڡ�",
    )
    assistant_agent = ChatAgent(
        system_message=assistant_sys_msg,
        model=ModelType.OPENAI, # ע�⣺��ʹ�Ǳ���ģ�ͣ�ֻҪ�ӿڼ��ݣ�������� ModelType.OPENAI
        model_config=dict(model=model_name), # ��ȷָ��ģ������
        task_prompt=task_prompt, # �� Agent ֪����������
    )

    # AI �û� Agent (��������ѧ��)
    user_sys_msg = BaseMessage.make_user_message(
        role_name="����ѧ��",
        content="��רע�������������ر�������ۺ�������ѧ���һ�ȷ�������еĿ�ѧ�������Ͻ��ͺ����ġ�",
    )
    user_agent = ChatAgent(
        system_message=user_sys_msg,
        model=ModelType.OPENAI,
        model_config=dict(model=model_name),
        task_prompt=task_prompt,
    )
    
    # 4. ���� Agent��׼����ʼ�Ի�
    assistant_agent.reset()
    user_agent.reset()

    # 5. ��ʼ���ֶԻ� (Role-Playing)
    # �����ȿ�ʼ����������뷨
    assistant_msg = assistant_agent.step(user_agent.system_message)
    print(f"��{assistant_agent.role_name}��: {assistant_msg.content}\n")

    # ���ƶԻ��ִΣ���������ѭ��
    for _ in range(5): # ����5�ֶԻ�
        # �û�������ѧ�ң��������ֵ��뷨���л�Ӧ������
        user_msg = user_agent.step(assistant_msg)
        print(f"��{user_agent.role_name}��: {user_msg.content}\n")
        
        # ���֣�С˵�ң��ٸ����û��ķ������д���
        assistant_msg = assistant_agent.step(user_msg)
        print(f"��{assistant_agent.role_name}��: {assistant_msg.content}\n")

    print("-" * 30)
    print("������ɣ�")

if __name__ == "__main__":
    main()