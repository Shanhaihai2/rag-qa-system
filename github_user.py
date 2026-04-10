import argparse
from utils import fetch_and_save_github_user

def main():
    """
    sys.argv写法
     # 检查是否提供了用户名
    if len(sys.argv) < 2:
        print("用法：python github_user.py <GitHub用户名>")
        print("示例：python github_user.py octocat")
        return
    
    username = sys.argv[1]
    print(f"正在获取用户 {username} 的信息...")
    
    success = fetch_and_save_github_user(username)
    
    if success:
        print(f"✅ 成功！信息已保存到 {username}.json")
    else:
        print(f"❌ 获取失败，请检查用户名或网络")
    """
    #argparse库写法
    parser = argparse.ArgumentParser(
        description="获取 GitHub 用户公开信息并保存为 JSON 文件"
    )
    parser.add_argument(
        "username",
        help="GitHub 用户名"
    )
    parser.add_argument(
        "-o", "--output",
        help="指定输出文件名（默认为 用户名.json）"
    )
    
    args = parser.parse_args()
    
    print(f"正在获取用户 {args.username} 的信息...")
    
    success = fetch_and_save_github_user(args.username, save_path=args.output)
    
    if success:
        output_file = args.output if args.output else f"{args.username}.json"
        print(f"✅ 成功！信息已保存到 {output_file}")
    else:
        print(f"❌ 获取失败，请检查用户名或网络")

if __name__ == "__main__":
    main()