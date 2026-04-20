from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np

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

#查看加载结果
print(f"√ 成功加载 PDF，共{len(documents)}页")
print("-" * 50)

#预览第一页内容
if documents:
    first_page = documents[0]
    print(f"第一页元数据：{first_page.metadata}")
    print(f"第一页内容预览（前三百字）:\n{first_page.page_content[:300]}")

print("\n" + "=" * 50)
print("使用 PDFPlumberLoader 加载同一文件：")

plumber_loader = PDFPlumberLoader(pdf_path)
docs_plumber = plumber_loader.load()

print(f"√ 成功加载，共{len(docs_plumber)}页")
if docs_plumber:
    print(f"第一页内容预览（前三百字）：\n{docs_plumber[0].page_content[:300]}")

#创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500, #每个块的目标字符数
    chunk_overlap = 50, #相邻块之间的重复字符数
    length_function = len, #计算长度的函数默认len
    separators = ["\n\n", "\n", "。", "！", "？", "；", "，" ," " ,""] #分割优先级
)

#将文档分割成块
chunks = text_splitter.split_documents(documents)

print(f"\n√ 文档已被分割为{len(chunks)}个文本块。")
print("-" * 50)

#预览前两个块
for i, chunk in enumerate(chunks[:2]):
    print(f"【块{i+1}】长度：{len(chunk.page_content)}字符")
    print(f"内容预览:{chunk.page_content[:50]}……")
    print("-" * 30)

# 假设 chunks 是第 17 天生成的分块列表
# 为前 3 个块生成向量（如果块数不足 3，则取全部）
sample_chunks = chunks[:3]
sample_texts = [chunk.page_content for chunk in sample_chunks]

# 生成向量
vectors = embeddings.embed_documents(sample_texts)

print(f"\n✅ 已为 {len(vectors)} 个文本块生成向量。")
print(f"每个向量的维度：{len(vectors[0])}")  # BGE-small 是 512 维
print(f"第一个向量的前 5 个值：{vectors[0][:5]}")

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

print("\n" + "="*50)
print("语义相似度测试：")
print(f"「苹果」与「香蕉」的相似度：{cosine_similarity(vecs[0], vecs[1]):.4f}")
print(f"「苹果」与「天气」的相似度：{cosine_similarity(vecs[0], vecs[2]):.4f}")
print(f"「香蕉」与「天气」的相似度：{cosine_similarity(vecs[1], vecs[2]):.4f}")
