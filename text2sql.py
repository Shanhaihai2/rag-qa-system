from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
import re

#初始化LLM（温度设为0，确保输出稳定）
llm = ChatOllama(model = "qwen2.5:7b",temperature=0)


#连接SQLite数据库
DB_PATH = "./data/ecommerce.db"
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

# 查看数据库中有哪些表
print(f"✅ 数据库连接成功！")
print(f"  表列表：{db.get_usable_table_names()}")
print(f"  各表信息：")
for table in db.get_usable_table_names():
    print(f"    {table}: {db.get_table_info([table])[:200]}...")

# 在 text2sql.py 中追加
result = db.run("SELECT pr.product_name, SUM(o.quantity) AS total_sold FROM orders o JOIN products pr ON o.product_id = pr.product_id GROUP BY pr.product_name ORDER BY total_sold DESC")
print("\n📊 产品销售统计：")
print(result)


def get_sql_from_question(question, db, llm):
    """
    根据自然语言问题生成 SQL 查询语句
    """
 # 获取完整的表结构信息（含 CREATE TABLE 语句和样例行）
    table_info = db.get_table_info()

    # 构造提示词
    prompt = f"""你是一个 SQL 专家。请根据以下数据库表结构，将用户问题转换成一条 SQLite 语法查询语句。
只输出 SQL 语句，不要带任何解释、markdown标记或分号后的内容。

数据库表结构：
{table_info}

用户问题：{question}
SQL:"""
    
    # 调用 LLM
    response = llm.invoke(prompt)
    raw_sql = response.content.strip()

    # 简单清洗：去掉可能的 markdown 标记和开头结尾空白
    raw_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
    # 清洗：去掉 "SQL: " 前缀（大小写不敏感）
    if raw_sql.upper().startswith("SQL:"):
        raw_sql = raw_sql[4:].strip()

    return raw_sql

def extract_sql(text):
    """从 LLM 输出中提取 SQL 语句"""
    # 匹配以 SELECT 开头、以分号或换行结束的语句
    match = re.search(r"(SELECT.*?;)", text, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else text


# 测试问题列表
test_questions = [
    "产品表里有多少种产品？",                          # 简单计数
    "价格大于100元的产品有哪些？",                     # 带条件
    "每个客户总共下了多少订单？",                     # 多表联查 + 聚合
    "销量最高的产品是什么？卖了多少个？",              # 排序 + 限制
    "2026年3月的订单总金额是多少？",                   # 日期过滤 + 求和
]

for q in test_questions:
    print(f"\n{'='*50}")
    print(f"问题：{q}")
    sql = extract_sql(get_sql_from_question(q, db, llm))
    print(f"生成的 SQL：{sql}")
    
    # 执行 SQL 并打印结果
    try:
        result = db.run(sql)
        print(f"执行结果：{result}")
    except Exception as e:
        print(f"执行出错：{e}")

def generate_answer_from_result(question, sql, result, llm):
    """
    根据用户问题、生成的 SQL、执行结果，用 LLM 生成自然语言回答
    """
    # 如果结果为空或出错，给出友好提示
    if result is None or result == "" or result == "[]":
        return "很抱歉，没有查询到相关数据，请检查您的查询条件。"
    
    summary_prompt = f"""你是一个数据分析助手。请根据以下信息，用简洁、流畅的中文回答用户的问题。
不要编造数据，只根据提供的查询结果作答。

用户问题：{question}
执行的 SQL：{sql}
查询结果：{result}

请用自然语言回答："""
    
    response = llm.invoke(summary_prompt)
    return response.content.strip()

def text2sql_qa(question, db, llm):
    """
    完整的 Text2SQL 问答流水线：
    问题 → 生成 SQL → 执行 SQL → 生成自然语言回答
    """
    # 1. 生成 SQL
    sql = get_sql_from_question(question, db, llm)
    print(f"生成的 SQL：{sql}")
    
    # 2. 执行 SQL
    try:
        result = db.run(sql)
        print(f"执行结果：{result}")
    except Exception as e:
        # 如果 SQL 执行失败，直接告诉用户并记录日志
        print(f"SQL 执行失败：{e}")
        return f"对不起，生成 SQL 时出错了。错误信息：{e}"
    
    if result == "" or result == "[]":
        return "很抱歉，没有查询到符合条件的数据。"

    # 3. 生成回答
    answer = generate_answer_from_result(question, sql, result, llm)
    return answer

if __name__ == "__main__":
    test_questions = [
        "产品表里有多少种产品？",
        "销量最高的产品是什么？卖了多少个？",
        "2026年3月的订单总金额是多少？",
        "所有订单的总金额是多少？",
    ]
    
    for q in test_questions:
        print(f"\n{'='*50}")
        print(f"❓ 用户问题：{q}")
        answer = text2sql_qa(q, db, llm)
        print(f"💬 AI 回答：{answer}")