class Document:
    """
    一个代表通用文档的类
    属性:
        content: 文档的文字内容（字符串）
        metadata: 文档的元数据（字典），比如作者、来源等
    """
    def __init__(self, content,metadata=None):
        self.content = content
        # 如果没有传metadata，就默认给一个空字典
        if metadata is None:
            self.metadata = {}
        else:
            self.metadata = metadata
            
    def summary(self, max_length=2):
        """
        返回文档内容的摘要（前 max_length 个字符）
        """
        if len(self.content) <= max_length:
            return self.content
        else:
            return self.content[:max_length] + "~"
            
class PDFDocument(Document):
    """
    代表一个 PDF 文档，继承自 Document
    额外属性:
        num_pages: 页数
    """
    def __init__(self, content, num_pages, metadata=None):
        # 调用父类 Document 的 __init__ 方法，初始化 content 和 metadata
        super().__init__(content, metadata)
        self.num_pages = num_pages

    def info(self):
        """返回 PDF 的简要信息"""
        return f"PDF文档，共 {self.num_pages} 页，作者：{self.metadata.get('author', '未知')}"