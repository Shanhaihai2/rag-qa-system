from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import numpy as np

CURRENT_MODEL = "qwen2.5:7b"  # 或 "qwen2.5:1.5b"
# 直接指定本地模型路径（使用绝对路径或相对路径）
model_path = "./models/bge-small-zh-v1.5"

#使用本地免费的中文Embedding模型
model_kwargs = {'device':'cpu'}#如果没有GPU，就用CPU
encode_kwargs = {'normalize_embeddings':True}#归一化向量，便于计算相似度

embeddings = HuggingFaceEmbeddings(
    model_name = model_path,
    model_kwargs = model_kwargs,
    encode_kwargs = encode_kwargs
)

print("√离线Embedding模型加载成功！")



#指定PDF文件路径
pdf_path = "data/yuanshen.pdf"

#创建加载器
loader = PyPDFLoader(pdf_path)

#加载文档
documents = loader.load()

# #查看加载结果
# print(f"√ 成功加载 PDF，共{len(documents)}页")
# print("-" * 50)

# #预览第一页内容
# if documents:
#     first_page = documents[0]
#     print(f"第一页元数据：{first_page.metadata}")
#     print(f"第一页内容预览（前三百字）:\n{first_page.page_content[:300]}")

# print("\n" + "=" * 50)
# print("使用 PDFPlumberLoader 加载同一文件：")

# plumber_loader = PDFPlumberLoader(pdf_path)
# docs_plumber = plumber_loader.load()

# print(f"√ 成功加载，共{len(docs_plumber)}页")
# if docs_plumber:
#     print(f"第一页内容预览（前三百字）：\n{docs_plumber[0].page_content[:300]}")

#创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500, #每个块的目标字符数
    chunk_overlap = 50, #相邻块之间的重复字符数
    length_function = len, #计算长度的函数默认len
    separators = ["\n\n", "\n", "。", "！", "？", "；", "，" ," " ,""] #分割优先级
)

#将文档分割成块
chunks = text_splitter.split_documents(documents)

# print(f"\n√ 文档已被分割为{len(chunks)}个文本块。")
# print("-" * 50)

# #预览前两个块
# for i, chunk in enumerate(chunks[:2]):
#     print(f"【块{i+1}】长度：{len(chunk.page_content)}字符")
#     print(f"内容预览:{chunk.page_content[:50]}……")
#     print("-" * 30)

# 假设 chunks 是第 17 天生成的分块列表
# 为前 3 个块生成向量（如果块数不足 3，则取全部）
sample_chunks = chunks[:3]
sample_texts = [chunk.page_content for chunk in sample_chunks]

# 生成向量
vectors = embeddings.embed_documents(sample_texts)

# print(f"\n✅ 已为 {len(vectors)} 个文本块生成向量。")
# print(f"每个向量的维度：{len(vectors[0])}")  # BGE-small 是 512 维
# print(f"第一个向量的前 5 个值：{vectors[0][:5]}")

def cosine_similarity(vec1, vec2):
    """计算两个向量的余弦相似度"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

#测试三组句子
sentences = [
    "苹果是一种很好吃的水果",
    "香蕉的味道也不错",
    "今天天气下雨不适合出去玩"
]

#生成向量
vecs = embeddings.embed_documents(sentences)

# print("\n" + "="*50)
# print("语义相似度测试：")
# print(f"「苹果」与「香蕉」的相似度：{cosine_similarity(vecs[0], vecs[1]):.4f}")
# print(f"「苹果」与「天气」的相似度：{cosine_similarity(vecs[0], vecs[2]):.4f}")
# print(f"「香蕉」与「天气」的相似度：{cosine_similarity(vecs[1], vecs[2]):.4f}")


# 指定持久化目录（向量数据将保存在这里）
persist_directory = "./chroma_db"

# 创建向量库
# 如果目录已存在，会自动加载；否则新建并向量化所有 chunks
vectordb = Chroma.from_documents(
    documents=chunks,               # 第17天生成的文本块列表
    embedding=embeddings,           # 第18天初始化好的 Embedding 模型
    persist_directory=persist_directory
)
# 查看库中的向量数量
# 注意：Chroma 新版本中 _collection 属性可能被标记为私有，可用 len(vectordb.get()['ids']) 替代
# try:
#     count = vectordb._collection.count()
# except AttributeError:
#     count = len(vectordb.get()['ids'])
# print(f"✅ 向量库已创建/加载，共包含 {count} 个向量。")

def retrieve_relevant_chunks(query: str, k: int = 3):
    """
    根据用户问题，从向量库中检索最相关的 k 个文本块
    """
    docs = vectordb.similarity_search(query, k=k)
    return docs

# #测试检索
# test_query = "七神分别是什么？" #请根据你的PDF内容提问
# results = retrieve_relevant_chunks(test_query, k=2)

# print("\n" + "=" * 50)
# print(f"测试问题：{test_query}")
# print(f"检索到{len(results)}个相关块:")
# for i, doc in enumerate(results):
#     source = doc.metadata.get('source', 'unknown')
#     page = doc.metadata.get('page', '?')
#     print(f"\n【块{i+1}】来源：{source}，页码：{page}")
#     print(f"内容预览：{doc.page_content[:200]}...")

#初始化本地Ollama模型
llm = ChatOllama(
    model = CURRENT_MODEL,
    temperature=0.7,
    num_predict=512,
)

print("√Ollama模型加载成功！")

# 提示模板
template = """你是一个专业的知识库问答助手。请仅根据以下上下文信息回答问题。如果上下文没有提供足够信息，请如实告知“根据现有资料无法回答”。
上下文：
{context}

问题：
{question}

回答："""

prompt = ChatPromptTemplate.from_template(template)

# 创建检索器
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# 构建 RAG 链
rag_chain = (
    {"context": retriever,"question":RunnablePassthrough()}#RunnablePassthrough可以让输入进来的字符串原封不动传给字典question键
    | prompt # |符号可以使|符号前的输出自动传到后的输入
    | llm
    | StrOutputParser()
)

print("√ RAG链构建完成！")

# # 测试完整 RAG 问答
# test_question = "原神的核心主题是啥"  # 请替换成实际问题
# print("\n" + "=" * 50)
# print(f"用户问题：{test_question}")
# print("正在生成回答，请稍候...")

# answer = rag_chain.invoke(test_question)

# print(f"\n回答：\n{answer}")

def rebuild_vectordb(chunk_size = 500, chunk_overlap = 50):
    """重建向量库，返回新的 vectordb 和 chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators = ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    #删除旧库
    import shutil
    shutil.rmtree("./chroma_db", ignore_errors=True)

    vectordb = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = "./chroma_db"
    )
    return vectordb, chunks

# test_questions = [
#     "七神分别是哪七个？",
#     "钟离是谁？",
#     "主角又是谁？"
# ]

# def evaluate_rag(vectordb, questions):
#     retriever = vectordb.as_retriever(search_type="similarity_score_threshold",search_kwargs={"score_threshold": 0.5,"k":3})
#     for q in questions:
#         docs = retriever.invoke(q)
#         print(f"问题：{q}")
#         for i, doc in enumerate(docs):
#             print(f" 块{i+1}：{doc.page_content[:80]}...")

# rebuild_vectordb(300,5)
# evaluate_rag(vectordb, test_questions)

def test_model(model_name, question):
    """用指定模型回答一个问题"""
    llm = ChatOllama(model=model_name, temperature=0.7, num_predict=512)
    # 临时构建一个链
    prompt = ChatPromptTemplate.from_template("""请根据以下上下文回答问题。
上下文：{context}
问题：{question}
回答：""")
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(question)
# # 对比测试
# test_q = "原神里面目前最厉害的是谁？"
# print("===== 1.5B 回答 =====")
# print(test_model("qwen2.5:1.5b", test_q))

# print("\n===== 7B 回答 =====")
# print(test_model("qwen2.5:7b", test_q))


# 在文件末尾（if __name__ == "__main__": 之前）确保 rag_chain 已定义
# 如果测试代码放在 if __name__ == "__main__": 里，rag_chain 需在外面定义