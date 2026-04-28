# 智能知识库问答系统 (RAG-QA-System)
基于 **RAG（检索增强生成）** 的本地知识库问答系统。上传 PDF 文档后，系统自动进行文本提取、语义向量化，并支持基于文档内容的自然语言问答。**全程本地运行，无需 API Key，数据安全可控。**

### 克隆项目
git clone https://github.com/shanhaihai2/rag-qa-system.git
cd rag-qa-system

## ✨ 核心功能
- 📄 支持 PDF 文档上传与自动解析
- 🧩 智能文本分块，保持语义完整性
- 🔢 本地 Embedding 模型，免费且隐私安全
- 🗄️ Chroma 向量数据库，持久化存储与快速检索
- 🦙 Ollama 本地大模型（Qwen2.5），无需联网
- 🚀 FastAPI 提供 RESTful API，自动生成 Swagger 文档
- 🔍 支持相似度检索、MMR 等检索策略
- 📊 完成分块策略对比优化实验

## 📁 项目结构
rag-qa-system/
├── api.py # FastAPI 应用入口
├── rag.py # RAG 核心逻辑（加载、分块、向量化、检索、问答）
├── evaluate.py # RAG 优化对比实验脚本
├── github_user.py # 命令行小工具（第一阶段）
├── utils.py # 工具函数
├── requirements.txt # Python 依赖清单
├── models/ # 本地 Embedding 模型文件（需手动下载）
├── chroma_db/ # Chroma 向量库持久化目录
├── data/ # 测试 PDF 文件
└── README.md

## 🛠️ 技术栈
| 层级 | 技术 |
| :--- | :--- |
| 后端框架 | FastAPI + Uvicorn |
| AI 框架 | LangChain + LCEL |
| 大语言模型 | Ollama + Qwen2.5 (1.5B) |
| Embedding | BAAI/bge-small-zh-v1.5（HuggingFace） |
| 向量数据库 | Chroma |
| 文档处理 | PyPDFLoader / PDFPlumberLoader |
| 前端（规划中） | Vue 3 + UniApp |

## 🏗️ 系统架构

## 🚀 快速开始

### 1. 环境要求
- Python 3.10+
- Ollama（用于本地运行大模型）
- Windows / macOS / Linux

### 2. 安装 Python 依赖
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

### 3. 下载 Embedding 模型
从 https://hf-mirror.com/BAAI/bge-small-zh-v1.5 下载所有文件，放入 models/bge-small-zh-v1.5/

### 4. 下载 LLM 模型
安装 Ollama 后：
ollama pull qwen2.5:1.5b

### 5. 启动服务
# 先启动 Ollama（从开始菜单）
# 再启动 FastAPI
uvicorn api:app --reload

### 6. 访问 API 文档
打开 http://127.0.0.1:8000/docs

## 📡 API 接口

| 方法 | 路径 | 说明 | 请求体 |
| :--- | :--- | :--- | :--- |
| GET | `/` | 根路径，返回欢迎信息 | - |
| GET | `/status` | 服务器状态 + 时间 | - |
| POST | `/qa` | 模拟问答（无 RAG） | `{"question": "..."}` |
| POST | `/rag/qa` | **RAG 知识库问答** | `{"question": "..."}` |
| POST | `/documents` | 上传文档 | `{"title": "...", "content": "..."}` |
| GET | `/documents` | 文档列表（分页） | 查询参数 `skip`, `limit` |
| GET | `/documents/{id}` | 文档详情 | - |

## 📊 优化记录
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

## 🩺 故障排查
| 现象 | 可能原因 | 解决方法 |
| :--- | :--- | :--- |
| `ConnectionError` / 无法连接 | Ollama服务未启动 | 启动Ollama桌面程序 |
| `Can't load model` | 本地Embedding模型缺失 | 重新下载并放入`models/`目录 |
| 检索返回空 | `score_threshold`过高或`chunk_size`过小 | 降低阈值或调整分块参数 |
| 回答与上下文无关 | 提示词模板设计不佳或检索不精准 | 优化prompt，强调“仅根据上下文回答” |

## 📅 开发计划
- [x] FastAPI 基础接口
- [x] CORS 跨域配置
- [x] 异常处理与日志
- [x] 接入 LangChain RAG
- [x] RAG 优化与对比实验
- [x] 接入 Text2SQL
- [x] LangGraph 工作流
- [ ] Vue 3 前端界面

## 📄 许可证


