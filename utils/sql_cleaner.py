# utils/sql_cleaner.py
import re

# 需要拦截的高危操作关键词
FORBIDDEN_KEYWORDS = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE']

def validate_sql(sql: str) -> bool:
    """
    检查 SQL 是否包含高危操作
    返回 True = 安全，False = 被拦截
    """
    upper_sql = sql.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        # \b 是单词边界，防止误判（如 'DELETE' 不会匹配到 'DELETE_OLD'）
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, upper_sql):
            return False
    return True

MAX_RETRIES = 2

def execute_sql_with_retry(sql: str, question: str, db, llm, retries=MAX_RETRIES):
    """
    执行 SQL，如果失败则让 LLM 根据错误信息修正 SQL，最多重试 retries 次
    """
    for attempt in range(retries + 1):
        try:
            result = db.run(sql)
            return result, sql  # 返回结果和最终执行的 SQL
        except Exception as e:
            if attempt < retries:
                # 构造纠错 Prompt，让 LLM 根据错误信息修正
                fix_prompt = f"""你生成的上一条SQL执行时发生错误。请修正SQL，只返回正确的SQL语句。

原始问题：{question}
错误SQL：{sql}
错误信息：{str(e)}

修正后的SQL："""
                sql = llm.invoke(fix_prompt).content.strip()
                sql = sql.replace("```sql", "").replace("```", "").strip()
                if sql.upper().startswith("SQL:"):
                    sql = sql[4:].strip()
            else:
                raise e
    return None, sql