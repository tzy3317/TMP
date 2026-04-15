#!/usr/bin/env python3
"""
OpenAI 兼容协议 LLM 聊天客户端（支持流式输出和历史记录）
功能：
1. 终端界面输入聊天内容
2. 支持流式输出（逐字显示）
3. 支持历史聊天记录自动添加到上下文
4. 直到用户按 Ctrl+C 退出终端
"""

import os
import json
import http.client
from urllib.parse import urlparse

def load_dotenv():
    """从项目根目录加载 .env 文件，返回字典"""
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    env_path = os.path.join(project_root, ".env")
    
    env_vars = {}
    if not os.path.exists(env_path):
        print(f"错误: .env 文件不存在于 {env_path}")
        return env_vars
    
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("\"'")
    except Exception as e:
        print(f"读取 .env 文件出错: {e}")
    return env_vars

def call_llm_stream(api_key, base_url, model, temperature, max_tokens, messages, timeout=30):
    """流式调用 LLM API"""
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = "/v1/chat/completions"  # 固定正确路径
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # 创建连接
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, timeout=timeout)
        
        # 发送请求
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        
        # 状态码检查
        if response.status != 200:
            print(f"\nAPI错误: {response.status} {response.reason}")
            print(f"返回内容: {response.read().decode('utf-8')}")
            conn.close()
            return None

        full_content = ""
        buffer = b""  # 使用字节缓冲，避免解码错误

        while True:
            chunk = response.read(1024)
            if not chunk:
                break
            
            buffer += chunk

            # 按行处理
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    line = line.decode("utf-8").strip()
                except:
                    continue

                if not line:
                    continue
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if "choices" in data:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                                full_content += content
                    except:
                        continue

        conn.close()
        return full_content

    except Exception as e:
        print(f"\n连接错误: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def main():
    print("=== LLM 聊天客户端（支持流式输出）===")
    print("按 Ctrl+C 退出聊天")
    print("====================================")
    
    env = load_dotenv()
    
    api_key = env.get("API_KEY", "dummy")
    base_url = env.get("BASE_URL")
    model_name = env.get("MODEL_NAME")
    temperature = float(env.get("TEMPERATURE", "0.7"))
    max_tokens = int(env.get("MAX_TOKENS", 2048))
    timeout = int(env.get("TIMEOUT", 60))

    if not base_url or not model_name:
        print("错误: 请在 .env 文件中设置 BASE_URL, MODEL_NAME")
        return

    print(f"使用模型: {model_name}")
    print(f"API URL: {base_url}")
    print()
    
    chat_history = []
    
    try:
        while True:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            
            chat_history.append({"role": "user", "content": user_input})
            if len(chat_history) > 10:
                chat_history = chat_history[-10:]
            
            print("助手: ", end="", flush=True)
            assistant_response = call_llm_stream(
                api_key, base_url, model_name, temperature, max_tokens, chat_history, timeout
            )
            
            if assistant_response:
                chat_history.append({"role": "assistant", "content": assistant_response})
            
            print("\n")
            
    except KeyboardInterrupt:
        print("\n\n退出聊天...")
        print("====================================")

if __name__ == "__main__":
    main()