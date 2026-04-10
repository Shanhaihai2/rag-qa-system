from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI(title="我的第一个 FastAPI 应用")

# 定义一个 GET 接口，路径为根路径 "/"
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# 定义一个带路径参数的接口
@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id, "name": f"用户{user_id}"}

# 定义一个带查询参数的接口
@app.get("/search")
def search_items(q: str = None, limit: int = 10):
    return {"query": q, "limit": limit}