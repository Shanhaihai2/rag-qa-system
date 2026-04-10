from utils import read_json, save_json, fetch_url, fetch_and_save_github_user
from models import Document, PDFDocument

"""
# 测试 1：保存一个字典为 JSON
test_data = {
    "name": "张三",
    "age": 20,
    "skills": ["Python", "Git", "FastAPI"]
}
save_json(test_data, "test.json")

# 测试 2：读取刚保存的 JSON 文件
loaded_data = read_json("test.json")
print("读取到的数据：", loaded_data)

# 测试 3：获取一个网页（用 GitHub 的公开 API 做测试）
url = "https://api.github.com/users/octocat"
content = fetch_url(url)
if content:
    print("成功获取网页内容，前 200 个字符：")
    print(content[:200])
else:
    print("获取网页失败")
"""
"""
doc1 = Document("Python有关内容", {"author":"小米","date":"2026-04-26"})
print(doc1.content)
print(doc1.metadata)
doc2 = Document("无元数据")
print(doc2.content)
print(doc2.metadata)

print(doc1.summary())
print(doc2.summary())

pdf = PDFDocument("PDF文件的内容是。。。。",10,{"author":"华为"})
print(pdf.content)
print(pdf.summary(3))
print(pdf.info()) 
"""     

# 测试获取 octocat（GitHub 官方示例账号）
success = fetch_and_save_github_user("shanhaihai2")

if success:
    print("用户信息已保存，请查看 octocat.json 文件")
else:
    print("获取用户信息失败")

# 再测试一个不存在的用户，看看异常处理是否正常
print("\n测试一个不存在的用户：")
fetch_and_save_github_user("this_user_does_not_exist_123456")
