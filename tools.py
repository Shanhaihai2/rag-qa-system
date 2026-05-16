# tools.py
from langchain_core.tools import Tool
from rag import rag_chain
from smart_qa import smart_qa_invoke

# 工具1：RAG 知识库问答
def rag_tool_func(query: str) -> str:
    """调用 RAG 链，返回答案"""
    return rag_chain.invoke(query)

rag_tool = Tool(
    name="知识库问答",
    description="当用户询问关于已上传PDF文档的具体内容时使用。输入应该是一个完整的问题。",
    func=rag_tool_func
)

# 工具2：Text2SQL 数据库查询
def text2sql_tool_func(query: str) -> str:
    """调用 Text2SQL 工作流，返回完整结果中的 answer 字段"""
    result = smart_qa_invoke(query)
    return result.get("answer", "查询失败，请检查问题或数据库连接。")

text2sql_tool = Tool(
    name="数据库查询",
    description="""当用户询问关于产品、订单、客户等数据库中的统计数据时使用。
输入应该是一个完整的问题，例如：
- "产品表里有多少种产品？"
- "销量最高的产品是什么？"
- "每个客户总共下了多少订单？"

数据库表结构如下：
- products 表：product_id（主键）, product_name（产品名称）, category（分类）, price（价格）
- customers 表：customer_id（主键）, customer_name（客户姓名）, city（城市）
- orders 表：order_id（主键）, customer_id（外键→customers）, product_id（外键→products）, quantity（数量）, order_date（订单日期）
""",
    func=text2sql_tool_func
)


tools = [rag_tool, text2sql_tool]