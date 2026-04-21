from fastapi import FastAPI,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from rag import rag_chain # 确保 rag.py 在项目根目录

# 文档模型（响应时返回）
class DocumentResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# 上传文档时的请求体模型
class DocumentCreate(BaseModel):
    title: str = Field(..., description="文档标题", min_length=1, max_length=200)
    content: str = Field(..., description="文档正文内容")

fake_documents_db: List[DocumentResponse] = []
doc_id_counter = 1

# 配置日志格式和级别
logging.basicConfig(
    level=logging.INFO,  # 设置最低输出级别，DEBUG < INFO < WARNING < ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

# 创建一个 FastAPI 应用实例
app = FastAPI(title="智能问数与知识库平台API", version="0.1.0")

# 自定义处理器：捕获 ValueError
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"参数值无效：{str(exc)}"}
    )

# 自定义处理器：覆盖默认的 500 错误
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 可以在这里记录日志
    print(f"全局异常捕获：{type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误，请稍后重试"}
    )

#会抛出ValueError的接口
@app.get("/test-error")
def test_error(value: int):
    if value < 0:
        raise ValueError("value 不能为负数")
    return {"value": value}

# # 假设有一个模拟的文档数据库
# fake_documents_db = {
#     1: {"id": 1, "title": "Python入门"},
#     2: {"id": 2, "title": "FastAPI实战"}
# }

# 配置 CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的前端地址
    allow_credentials=True,       # 允许携带 Cookie
    allow_methods=["*"],          # 允许所有 HTTP 方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],          # 允许所有请求头
)

# 定义一个 Pydantic 模型，描述问答请求的数据结构
class QuestionRequest(BaseModel):
    question: str = Field(..., description="用户问题", min_length=1)# 必填，字符串类型
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

# @app.get("/documents/{doc_id}")
# def get_document(doc_id: int):
#     return {"doc_id": doc_id, "title": f"文档 {doc_id}"}

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents(skip: int = 0, limit: int = 10, db: DBSession = Depends(get_db)):
    """
    获取文档列表（分页）
    """
    logger.info(f"查询文档列表，skip={skip}, limit={limit}")
    db.query(f"SELECT * FROM documents LIMIT {limit} OFFSET {skip}")
    return fake_documents_db[skip : skip + limit]

@app.get("/status")
def get_server_status(current_time: str = Depends(get_current_time)):
    """
    获取服务器状态（演示依赖注入）
    """
    logger.info(f"有人访问了 /status 接口")  # INFO 级别
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
def ask_question(request: QuestionRequest, db: DBSession = Depends(get_db)):
    """
    知识库问答接口（当前为模拟实现）
    """
    logger.info(f"收到问答请求：{request.question[:50]}...")
    
    # 模拟检索相关文档（后续替换为 RAG 检索）
    related_docs = [doc.title for doc in fake_documents_db[:2]]
    
    # 模拟生成答案
    answer = f"关于「{request.question}」，知识库中有以下相关文档：{', '.join(related_docs) if related_docs else '暂无'}。这是一个模拟回答，后续将接入大模型。"
    
    return {
        "question": request.question,
        "answer": answer,
        "related_documents": related_docs,
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

@app.post("/documents", response_model=DocumentResponse, status_code=201)
def create_document(doc_in: DocumentCreate, db: DBSession = Depends(get_db)):
    """
    上传新文档
    """
    global doc_id_counter
    logger.info(f"正在创建新文档，标题：{doc_in.title}")
    
    new_doc = DocumentResponse(
        id=doc_id_counter,
        title=doc_in.title,
        content=doc_in.content,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    doc_id_counter += 1
    fake_documents_db.append(new_doc)
    
    # 模拟数据库插入日志
    db.query(f"INSERT INTO documents (title, content) VALUES ('{doc_in.title}', ...)")
    
    return new_doc

@app.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: DBSession = Depends(get_db)):
    """
    根据 ID 获取文档
    """
    logger.debug(f"查询文档 ID: {doc_id}")  # DEBUG 级别，默认不显示（level=INFO）
    db.query(f"SELECT * FROM documents WHERE id = {doc_id}")
    for doc in fake_documents_db:
        if doc.id == doc_id:
            return doc
    logger.warning(f"文档 {doc_id} 不存在")
    raise HTTPException(status_code=404, detail=f"文档 ID {doc_id} 不存在")

@app.post("/rag/qa")
async def rag_qa(request: QuestionRequest):
    """
    RAG 知识库问答接口
    """
    try:
        answer = rag_chain.invoke(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        logger.error(f"RAG 问答失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))