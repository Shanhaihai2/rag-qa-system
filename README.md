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

## 优化记录

### 分块策略对比

| chunk_size | chunk_overlap | 检索相关性评分 (1-5) | 备注 |
| :--- | :--- | :--- | :--- |
| 50 | 5 | 3.5 | 块太碎，上下文丢失 |
| 300 | 30 | 4.2 | **当前最佳**，平衡粒度与语义 |
| 500 | 50 | 3.8 | 块过大，检索精度下降 |

### 检索策略对比

| 策略 | 参数 | 评分 | 备注 |
| :--- | :--- | :--- | :--- |
| 相似度检索 | k=3 | 4.0 | 稳定 |
| MMR | k=3, fetch_k=5 | 4.1 | 多样性提升，但稍慢 |
| 带阈值相似度 | k=3, threshold=0.4 | 3.5 | 过滤过严，部分问题无结果 |

## 开发计划
- [x] FastAPI 基础接口
- [x] CORS 跨域配置
- [x] 异常处理与日志
- [x] 接入 LangChain RAG
- [ ] 接入 Text2SQL
- [ ] Vue 3 前端界面

## 故障排查 (Troubleshooting)

| 现象 | 可能原因 | 解决方法 |
| :--- | :--- | :--- |
| `ConnectionError` / 无法连接 | Ollama服务未启动 | 启动Ollama桌面程序 |
| `Can't load model` | 本地Embedding模型缺失 | 重新下载并放入`models/`目录 |
| 检索返回空 | `score_threshold`过高或`chunk_size`过小 | 降低阈值或调整分块参数 |
| 回答与上下文无关 | 提示词模板设计不佳或检索不精准 | 优化prompt，强调“仅根据上下文回答” |