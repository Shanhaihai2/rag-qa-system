from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. 定义状态结构
class WorkflowState(TypedDict):
    question: str
    answer: str
    steps: list

# 2. 定义三个节点函数
def step_analyze(state: WorkflowState):
    state["steps"].append("分析意图")
    return state

def step_process(state: WorkflowState):
    state["steps"].append("处理问题")
    state["answer"] = f"这是关于「{state['question']}」的模拟回答"
    return state

def step_summarize(state: WorkflowState):
    state["steps"].append("汇总输出")
    return state


# 3. 构建图
graph = StateGraph(WorkflowState)
graph.add_node("analyze", step_analyze)
graph.add_node("process", step_process)
graph.add_node("summarize", step_summarize)

graph.set_entry_point("analyze")
graph.add_edge("analyze", "process")
graph.add_edge("process", "summarize")
graph.add_edge("summarize", END)

app = graph.compile()

# 4. 测试
result = app.invoke({"question": "今天天气怎么样？", "steps": []})
print(f"答案：{result['answer']}")
print(f"执行步骤：{result['steps']}")


class SmartState(TypedDict):
    question: str
    intent: str
    answer: str
    steps: list

def detect_intent(state: SmartState):
    """模拟意图识别"""
    state["steps"].append("识别意图")
    # 简单模拟：如果问题里包含“数据/查询/订单/产品”等词，认为是查数据库
    keywords = ["数据", "查询", "订单", "产品", "价格", "销量"]
    if any(kw in state["question"] for kw in keywords):
        state["intent"] = "query_db"
    else:
        state["intent"] = "chat"
    return state

def route_by_intent(state: SmartState):
    """根据意图决定下一步"""
    if state["intent"] == "query_db":
        return "query_db"
    else:
        return "chat"
    
def node_query_db(state: SmartState):
    state["steps"].append("查询数据库")
    state["answer"] = f"[模拟查询结果] 关于「{state['question']}」的数据已返回"
    return state    

def node_chat(state: SmartState):
    state["steps"].append("闲聊回复")
    state["answer"] = f"你好！关于「{state['question']}」，我来陪你聊聊~"
    return state

# 构建条件图
graph = StateGraph(SmartState)
graph.add_node("detect", detect_intent)
graph.add_node("query_db", node_query_db)
graph.add_node("chat", node_chat)

graph.set_entry_point("detect")
graph.add_conditional_edges(
    "detect",
    route_by_intent,
    {"query_db": "query_db", "chat": "chat"}
)
graph.add_edge("query_db", END)
graph.add_edge("chat", END)

app = graph.compile()

# 测试两个不同类型的问题
print("="*50)
test1 = app.invoke({"question": "今天天气怎么样？", "steps": []})
print(f"问题：{test1['question']}")
print(f"意图：{test1['intent']}")
print(f"回答：{test1['answer']}")

print("="*50)
test2 = app.invoke({"question": "产品表里有多少种产品？", "steps": []})
print(f"问题：{test2['question']}")
print(f"意图：{test2['intent']}")
print(f"回答：{test2['answer']}")