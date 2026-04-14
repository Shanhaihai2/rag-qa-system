from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI(title="智能问数与知识库平台API", version="0.1.0")

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
