from fastapi import FastAPI,Depends
from pydantic import BaseModel, Field
from datetime import datetime

# 创建一个 FastAPI 应用实例
app = FastAPI(title="智能问数与知识库平台API", version="0.1.0")

# 定义一个 Pydantic 模型，描述问答请求的数据结构
class QuestionRequest(BaseModel):
    question: str = Field(..., description="用户输入的自然语言问题", min_length=1)# 必填，字符串类型
    max_tokens: int = Field(500, description="生成回答的最大 token 数", ge=1, le=2000)# 可选，默认 500
    temperature: float = Field(0.7, description="采样温度，控制随机性", ge=0.0, le=2.0)# 可选，默认 0.7
"""
Text2SQL嵌套模型
class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str
    database: str

class Text2SQLRequest(BaseModel):
    question: str
    db_config: DatabaseConfig
    max_results: int = 10
"""
class DBSession:
    """
    模拟的数据库会话类
    """
    def __init__(self):
        self.connected = True
        print("数据库会话已打开")

    def close(self):
        self.connected = False
        print("数据库会话已关闭")

    def query(self, sql: str):
        if not self.connected:
            raise Exception("会话已关闭")
        return f"执行查询：{sql}，返回模拟结果"

def get_db():
    """
    依赖函数：创建并提供一个数据库会话，结束后自动关闭
    """
    db = DBSession()
    try:
        yield db   # yield 表示这个依赖有“清理”逻辑
    finally:
        db.close()

def get_current_time():
    """
    依赖函数：返回当前服务器时间
    """
    return datetime.now().isoformat()


# 定义一个 GET 接口，路径为根路径 "/"
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!我的第一个接口跑起来了。"}

@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    return {"doc_id": doc_id, "title": f"文档 {doc_id}"}

@app.get("/documents")
def list_documents(skip: int = 0, limit: int = 10):
    # 模拟分页逻辑
    all_docs = [{"id": i, "title": f"文档{i}"} for i in range(1, 101)]
    return all_docs[skip : skip + limit]

@app.get("/status")
def get_server_status(current_time: str = Depends(get_current_time)):
    """
    获取服务器状态（演示依赖注入）
    """
    return {
        "status": "running",
        "server_time": current_time
    }

@app.get("/documents-db")
def list_documents_from_db(db: DBSession = Depends(get_db)):
    """
    通过注入的数据库会话查询文档列表（模拟）
    """
    result = db.query("SELECT * FROM documents")
    return {"db_connected": db.connected, "result": result}

@app.post("/qa")
def ask_question(request: QuestionRequest):
    """
    问答接口（目前返回模拟答案，后续接 Text2SQL 或 RAG）
    接收一个 JSON 请求体，符合 QuestionRequest 模型的结构
    """
    # 模拟处理逻辑
    answer = f"您的问题是：{request.question}。这是一个模拟回答，后续将接入真实 AI 模型。"
    
    return {
        "question": request.question,
        "answer": answer,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature
    }
"""
Text2SQL嵌套模型
@app.post("/text2sql")
def text_to_sql(request: Text2SQLRequest):
    # 可以通过 request.db_config.host 访问嵌套数据
    return {"sql": f"SELECT * FROM table WHERE question='{request.question}'"}
"""