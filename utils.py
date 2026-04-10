import json
import requests

def read_json(file_path):
    """
    读取 JSON 文件并返回字典
    参数:
        file_path: JSON 文件的路径（字符串）
    返回:
        解析后的字典，如果文件不存在或格式错误则返回 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 不是合法的 JSON 格式")
        return None
    
def save_json(data, file_path):
    """
    将字典保存为 JSON 文件
    参数:
        data: 要保存的字典
        file_path: 保存路径
    返回:
        成功返回 True，失败返回 False
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"成功保存到 {file_path}")
        return True
    except Exception as e:
        print(f"保存失败：{e}")
        return False
    
def fetch_url(url):
    """
    发送 GET 请求，返回响应内容
    参数:
        url: 要请求的网址
    返回:
        成功返回文本内容（字符串），失败返回 None
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果状态码不是 200，主动抛出异常
        return response.text
    except requests.exceptions.Timeout:
        print(f"请求超时：{url} 超过 10 秒未响应")
        return None
    except requests.exceptions.ConnectionError:
        print(f"网络连接错误，请检查网络或 URL：{url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误：{e}")
        return None
    except Exception as e:
        print(f"未知错误：{e}")
        return None
    
def get_github_user(username):
    """
    获取指定GitHub用户的公开信息
    参数：
        username：GitHub 用户名（字符串）
    返回：
        成功返回解析后的字典，失败返回None
    """
    url = f"https://api.github.com/users/{username}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            print(f"用户 {username} 不存在")
            return None
        elif response.status_code == 403:
            print("API 访问频率受限，请稍后再试")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"请求超时：GitHub API 响应太慢")
        return None
    except requests.exceptions.ConnectionError:
        print(f"网络连接错误，请检查网络")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误：{e}")
        return None
    except Exception as e:
        print(f"未知错误：{e}")
        return None
    
def fetch_and_save_github_user(username, save_path=None):
    """
    获取 GitHub 用户信息，提取关键字段，保存为 JSON 文件
    参数:
        username: GitHub 用户名
        save_path: 保存路径，默认为 {username}.json
    返回:
        成功返回 True，失败返回 False
    """
    if save_path is None:
        save_path = f"{username}.json"
    
    user_data = get_github_user(username)
    if user_data is None:
        return False
    
    # 提取我们关心的字段
    extracted = {
        "username": user_data.get("login"),
        "name": user_data.get("name"),
        "bio": user_data.get("bio"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "following": user_data.get("following"),
        "avatar_url": user_data.get("avatar_url"),
        "html_url": user_data.get("html_url")
    }

    # 复用我们第2天写的 save_json 函数
    return save_json(extracted, save_path)

def greet(name):
    """
    一个简单的打招呼函数（假装是新功能）
    """
    return f"你好，{name}！欢迎使用我的系统。"