import subprocess
import json
import os
import sys

def load_dotenv():
    """
    加载 .env 文件中的环境变量
    """
    env = {}
    # 获取当前脚本所在目录
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    # 寻找 .env 文件（优先在项目根目录，其次在脚本目录）
    env_path = os.path.join(os.path.dirname(script_dir), ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(script_dir, ".env")
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 去除首尾引号和空格
                    value = value.strip().strip('\'"')
                    env[key.strip()] = value
    return env

def anythingllm_query(message, timeout=30):
    """
    调用AnythingLLM的聊天API接口，返回干净的回答
    """
    # 加载环境变量
    env = load_dotenv()
    api_key = env.get("ANYTHINGLLM_API_KEY")
    workspace_slug = env.get("ANYTHINGLLM_WORKSPACE_SLUG")
    
    if not api_key:
        return "❌ 错误: 请在 .env 文件中设置 ANYTHINGLLM_API_KEY"
    if not workspace_slug:
        return "❌ 错误: 请在 .env 文件中设置 ANYTHINGLLM_WORKSPACE_SLUG"
    
    # API 地址
    api_url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    # 请求参数
    payload = {
        "message": message
    }
    
    # 构建 curl 命令
    cmd = [
        "curl",
        "-s",
        "-m", str(timeout),
        "-X", "POST",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload, ensure_ascii=False),
        api_url
    ]
    
    try:
        # 执行命令
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        stdout, stderr = proc.communicate()
        
        if proc.returncode == 0:
            try:
                # 解析 JSON
                json_resp = json.loads(stdout.decode('utf-8').strip())
                
                # 错误处理
                if json_resp.get("error"):
                    return f"❌ API错误: {json_resp['error']}"
                
                # 提取核心回答
                answer = json_resp.get("textResponse", "⚠️ 未获取到回答")
                
                # 提取参考文档
                sources = json_resp.get("sources", [])
                if sources:
                    docs = list(set(s.get("title") for s in sources))
                    answer += f"\n\n📖 参考文档：{', '.join(docs)}"
                
                return answer
            
            except json.JSONDecodeError:
                return f"⚠️ 响应解析失败：{stdout.decode('utf-8', errors='ignore')}"
        else:
            return f"⚠️ 请求失败：{stderr.decode('utf-8', errors='ignore')}"
    
    except Exception as e:
        return f"⚠️ 运行异常：{str(e)}"

def main():
    """
    主程序：交互式聊天
    """
    print("=== AnythingLLM 查询客户端 ===")
    print("按 Ctrl+C 退出")
    print("=" * 35)
    
    while True:
        try:
            user_input = input("\n你: ")
            if not user_input:
                continue
            
            print("\n助手: 正在思考中...", end="\r")
            response = anythingllm_query(user_input)
            
            # 清空加载提示
            print(" " * 30, end="\r")
            print(f"助手: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 已退出程序")
            sys.exit(0)
        except Exception as e:
            print(f"\n⚠️ 异常：{e}")

if __name__ == "__main__":
    main() 