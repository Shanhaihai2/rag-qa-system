from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader

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
