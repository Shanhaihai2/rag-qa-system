from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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