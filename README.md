# 智能问数与知识库平台 API

基于 FastAPI 构建的知识库问答系统后端，支持文档管理、智能问答（开发中）。

## 技术栈
- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn
- （后续）LangChain + RAG + Text2SQL

## 快速开始

### 1. 克隆项目
git clone https://github.com/你的用户名/rag-qa-system.git
cd rag-qa-system

### 2. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

### 3. 启动服务
uvicorn api:app --reload

### 4. 访问 API 文档
打开浏览器访问 http://127.0.0.1:8000/docs

### 5.下载 Embedding 模型
从 https://hf-mirror.com/BAAI/bge-small-zh-v1.5 下载所有文件，放置于 `models/bge-small-zh-v1.5/` 目录下。

## 主要接口
- `POST /documents` - 上传文档
- `GET /documents` - 文档列表（分页）
- `GET /documents/{id}` - 文档详情
- `POST /qa` - 知识库问答（模拟）

## 项目结构
.
├── api.py # FastAPI 应用入口
├── requirements.txt # 项目依赖
├── utils.py # 工具函数（第一阶段）
├── github_user.py # 命令行工具（第一阶段）
└── README.md # 项目说明

## 开发计划
- [x] FastAPI 基础接口
- [x] CORS 跨域配置
- [x] 异常处理与日志
- [ ] 接入 LangChain RAG
- [ ] 接入 Text2SQL
- [ ] Vue 3 前端界面