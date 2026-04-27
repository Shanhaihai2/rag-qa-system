from langgraph.graph import StateGraph, END
from typing import TypedDict
from text2sql import get_sql_from_question
# 导入 LLM 和数据库（从 text2sql.py 中复用）
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase

llm = ChatOllama(model="qwen2.5:7b", temperature=0)
DB_PATH = "./data/ecommerce.db"
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

class QAState(TypedDict):
    question: str          # 用户原始问题
    intent: str            # 意图："query_db" 或 "chat"
    sql: str               # 生成的 SQL
    query_result: str      # 数据库执行结果
    answer: str            # 最终回答
    error: str             # 错误信息（如有）

# 节点1：意图识别
def detect_intent(state: QAState):
    """根据关键词判断用户意图"""
    question = state["question"]
    keywords = ["产品", "订单", "客户", "价格", "销量", "数据", "查询", 
                "有多少", "统计", "金额", "哪些", "最", "排行"]
    if any(kw in question for kw in keywords):
        state["intent"] = "query_db"
    else:
        state["intent"] = "chat"
    return state

# 路由函数：根据意图决定下一步
def route_by_intent(state: QAState):
    if state["intent"] == "query_db":
        return "generate_sql"
    else:
        return "chat_reply"

# 节点2：闲聊回复
def chat_reply(state: QAState):
    state["answer"] = "你好！我是智能问数助手，可以帮你查询数据库中的产品、订单、客户等信息。请问有什么可以帮你的？"
    return state

# 节点3：生成 SQL
def generate_sql(state: QAState):
    """调用第30天写的 get_sql_from_question"""
    try:
        sql = get_sql_from_question(state["question"], db, llm)
        state["sql"] = sql
    except Exception as e:
        state["error"] = f"SQL 生成失败：{e}"
        state["sql"] = ""
    return state

# 路由函数：SQL 生成后判断是否成功
def route_after_generate(state: QAState):
    if state["error"] or not state["sql"]:
        return "handle_error"
    return "execute_sql"

# 节点4：执行 SQL
def execute_sql(state: QAState):
    """执行 SQL 并获取结果"""
    try:
        result = db.run(state["sql"])
        state["query_result"] = str(result) if result else "查询结果为空"
    except Exception as e:
        state["error"] = f"SQL 执行失败：{e}"
        state["query_result"] = ""
    return state

# 路由函数：执行后判断是否成功
def route_after_execute(state: QAState):
    if state["error"]:
        return "handle_error"
    return "summarize"

# 节点5：汇总结果
def summarize(state: QAState):
    """将查询结果总结成自然语言"""
    if state["query_result"] == "查询结果为空":
        state["answer"] = "很抱歉，没有查询到符合条件的数据。"
        return state
    
    summary_prompt = f"""你是一个数据分析助手。请根据以下信息，用简洁流畅的中文回答用户问题。

用户问题：{state['question']}
执行 SQL：{state['sql']}
查询结果：{state['query_result']}

请用自然语言回答："""
    
    response = llm.invoke(summary_prompt)
    state["answer"] = response.content.strip()
    return state

# 节点6：错误处理
def handle_error(state: QAState):
    state["answer"] = f"抱歉，处理您的问题时遇到了问题：{state.get('error', '未知错误')}。请检查您的查询或稍后重试。"
    return state

# 构建图
graph = StateGraph(QAState)

# 添加节点
graph.add_node("detect_intent", detect_intent)
graph.add_node("chat_reply", chat_reply)
graph.add_node("generate_sql", generate_sql)
graph.add_node("execute_sql", execute_sql)
graph.add_node("summarize", summarize)
graph.add_node("handle_error", handle_error)

# 设置入口
graph.set_entry_point("detect_intent")

# 意图路由
graph.add_conditional_edges(
    "detect_intent",
    route_by_intent,
    {"generate_sql": "generate_sql", "chat_reply": "chat_reply"}
)

# 生成 SQL 后的路由
graph.add_conditional_edges(
    "generate_sql",
    route_after_generate,
    {"execute_sql": "execute_sql", "handle_error": "handle_error"}
)

# 执行 SQL 后的路由
graph.add_conditional_edges(
    "execute_sql",
    route_after_execute,
    {"summarize": "summarize", "handle_error": "handle_error"}
)

# 终止边
graph.add_edge("chat_reply", END)
graph.add_edge("summarize", END)
graph.add_edge("handle_error", END)

# 编译
app = graph.compile()

# 测试
if __name__ == "__main__":
    test_questions = [
        "今天天气怎么样？",                    # 闲聊
        "产品表里有多少种产品？",              # 查数据
        "销量最高的产品是什么？",              # 查数据
    ]
    
    for q in test_questions:
        print(f"\n{'='*60}")
        result = app.invoke({"question": q, "sql": "", "query_result": "", "answer": "", "error": ""})
        print(f"❓ 问题：{result['question']}")
        print(f"🎯 意图：{result['intent']}")
        if result.get("sql"):
            print(f"📝 SQL：{result['sql']}")
            print(f"📊 结果：{result['query_result']}")
        print(f"💬 回答：{result['answer']}")