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