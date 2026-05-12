from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder
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



#创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500, #每个块的目标字符数
    chunk_overlap = 50, #相邻块之间的重复字符数
    length_function = len, #计算长度的函数默认len
    separators = ["\n\n", "\n", "。", "！", "？", "；", "，" ," " ,""] #分割优先级
)

#将文档分割成块
chunks = text_splitter.split_documents(documents)

# 指定持久化目录（向量数据将保存在这里）
persist_directory = "./chroma_db"

# 创建向量库
# 如果目录已存在，会自动加载；否则新建并向量化所有 chunks
vectordb = Chroma.from_documents(
    documents=chunks,               # 第17天生成的文本块列表
    embedding=embeddings,           # 第18天初始化好的 Embedding 模型
    persist_directory=persist_directory
)


def retrieve_relevant_chunks(query: str, k: int = 3):
    """
    根据用户问题，从向量库中检索最相关的 k 个文本块
    """
    docs = vectordb.similarity_search(query, k=k)
    return docs


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

def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        raise ValueError("PDF文件为空或无法解析!")
    chunks = text_splitter.split_documents(documents)
    vectordb = Chroma.from_documents(
    documents=chunks,               # 第17天生成的文本块列表
    embedding=embeddings,           # 第18天初始化好的 Embedding 模型
    persist_directory=persist_directory
    )
    return len(chunks)

# 1. 构建 BM25 关键词检索器 (基于你第17天生成的那堆 chunks)
bm25_retriever = BM25Retriever.from_documents(chunks)  # 这个 chunks 是你之前就生成好的
bm25_retriever.k = 5  # 让它先返回 5 个候选

# 2. 获取你原有的 Chroma 语义检索器
chroma_retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# 3. 🚀 混合检索函数 (手动实现，简单又稳定)
def get_ensemble_docs(query):
    # 3.1 分别获取两种结果
    bm25_docs = bm25_retriever.invoke(query)
    chroma_docs = chroma_retriever.invoke(query)
    
    # 3.2 用最简单的方式去重合并：一个放前面，另一个的补在后面
    combined = list(bm25_docs)
    for doc in chroma_docs:
        if doc not in combined:
            combined.append(doc)
    return combined

# 4. 🎯 重排序器 (使用最老牌的 bge-reranker-base 模型)
reranker_model = CrossEncoder('./models/bge-reranker-base', max_length=512)

def get_reranked_docs(query, top_n=3):
    # 4.1 先通过混合检索拿到一批候选文档
    candidate_docs = get_ensemble_docs(query)
    if not candidate_docs:
        return []
    
    # 4.2 准备好 (问题, 文档内容) 对，交给重排序模型打分
    pairs = [[query, doc.page_content] for doc in candidate_docs]
    scores = reranker_model.predict(pairs)
    
    # 4.3 根据分数从高到低排序，并选出前 top_n 个
    scored_docs = list(zip(scores, candidate_docs))
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored_docs[:top_n]]

print("✅ 第三阶段：混合检索与重排序模块已就绪！")


if __name__ == "__main__":
    test_query = "原神中的七神是谁？"
    print("\n===== 🧪 检索效果对比 =====")

    # 对比1：纯语义检索
    print("\n🔹 纯语义检索 (优化前)：")
    old_docs = chroma_retriever.invoke(test_query)
    for i, doc in enumerate(old_docs[:3]):
        print(f"{i+1}. {doc.page_content[:100]}...")

    # 对比2：混合检索 (优化后，无重排)
    print("\n🔹 混合检索 (优化后，无重排)：")
    ensemble_docs = get_ensemble_docs(test_query)
    for i, doc in enumerate(ensemble_docs[:3]):
        print(f"{i+1}. {doc.page_content[:100]}...")

    # 对比3：混合检索 + 重排序 (最终优化)
    print("\n🔹 混合检索 + 重排序 (最终优化)：")
    reranked_docs = get_reranked_docs(test_query)
    for i, doc in enumerate(reranked_docs):
        print(f"{i+1}. {doc.page_content[:100]}...")
