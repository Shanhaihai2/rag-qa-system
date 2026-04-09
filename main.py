from utils import read_json, save_json, fetch_url

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