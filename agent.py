# agent.py
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from tools import tools
import os

# 1. 初始化 LLM
agent_llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
    temperature=0
)

# 2. 创建 Agent (全新API)
agent = create_agent(
    agent_llm,
    tools,
    system_prompt="你是一个智能助手。根据用户的问题，自主选择并调用最合适的工具来获取信息，最后组织成通顺、友好的中文回答。如果无法使用工具，请直接用自己的知识回答。"
)