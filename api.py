from fastapi import FastAPI

# 创建一个 FastAPI 应用实例
app = FastAPI(title="智能问数与知识库平台API", version="0.1.0")

# 定义一个 GET 接口，路径为根路径 "/"
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!我的第一个接口跑起来了。"}
