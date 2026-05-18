#!/usr/bin/env python3
"""
OpenAI 兼容协议 LLM 聊天客户端（支持工具调用）
修复：curl_request 兼容所有系统
"""

import os
import json
import http.client
from urllib.parse import urlparse

def load_dotenv():
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

def list_files(directory):
    try:
        if not os.path.exists(directory):
            return f"错误: 目录 {directory} 不存在"
        
        files_info = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files_info.append({
                    "name": item,
                    "type": "file",
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                })
            elif os.path.isdir(item_path):
                files_info.append({
                    "name": item,
                    "type": "directory"
                })
        
        return json.dumps(files_info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"错误: {str(e)}"

def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(old_path):
            return f"错误: 文件 {old_path} 不存在"
        if os.path.exists(new_path):
            return f"错误: 目标文件 {new_path} 已存在"
        
        os.rename(old_path, new_path)
        return f"成功: 文件已重命名为 {new_name}"
    except Exception as e:
        return f"错误: {str(e)}"

def delete_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        
        if not os.path.exists(file_path):
            return f"错误: 文件 {file_path} 不存在"
        if not os.path.isfile(file_path):
            return f"错误: {file_path} 不是文件"
        
        os.remove(file_path)
        return f"成功: 文件已删除"
    except Exception as e:
        return f"错误: {str(e)}"

def create_file(directory, file_name, content):
    try:
        if not os.path.exists(directory):
            return f"错误: 目录 {directory} 不存在"
        
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            return f"错误: 文件 {file_path} 已存在"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"成功: 文件已创建"
    except Exception as e:
        return f"错误: {str(e)}"

def read_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        
        if not os.path.exists(file_path):
            return f"错误: 文件 {file_path} 不存在"
        if not os.path.isfile(file_path):
            return f"错误: {file_path} 不是文件"
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"错误: {str(e)}"

def curl_request(url, timeout=30):
    """兼容所有 Python 版本的 curl 请求"""
    try:
        import subprocess
        cmd = ["curl", "-s", "-m", str(timeout), url]
        
        # 使用字节模式读取，避免编码问题
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = proc.communicate()
        
        if proc.returncode == 0:
            # 尝试用utf-8解码，失败则用gbk
            try:
                return stdout.decode('utf-8').strip()
            except UnicodeDecodeError:
                return stdout.decode('gbk', errors='ignore').strip()
        else:
            # 尝试用utf-8解码错误信息，失败则用gbk
            try:
                return f"curl 错误: {stderr.decode('utf-8').strip()}"
            except UnicodeDecodeError:
                return f"curl 错误: {stderr.decode('gbk', errors='ignore').strip()}"
    except Exception as e:
        return f"请求失败: {str(e)}"

def call_llm_stream(api_key, base_url, model, temperature, max_tokens, messages, timeout=120):
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = "/v1/chat/completions"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "列出目录下的文件",
                    "parameters": {
                        "type": "object",
                        "properties": {"directory": {"type": "string"}},
                        "required": ["directory"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "rename_file",
                    "parameters": {
                        "type": "object",
                        "properties": {"directory": {"type": "string"}, "old_name": {"type": "string"}, "new_name": {"type": "string"}},
                        "required": ["directory", "old_name", "new_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "parameters": {
                        "type": "object",
                        "properties": {"directory": {"type": "string"}, "file_name": {"type": "string"}},
                        "required": ["directory", "file_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "parameters": {
                        "type": "object",
                        "properties": {"directory": {"type": "string"}, "file_name": {"type": "string"}, "content": {"type": "string"}},
                        "required": ["directory", "file_name", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "parameters": {
                        "type": "object",
                        "properties": {"directory": {"type": "string"}, "file_name": {"type": "string"}},
                        "required": ["directory", "file_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "curl_request",
                    "description": "通过curl访问网页并返回内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "timeout": {"type": "integer", "default": 30}
                        },
                        "required": ["url"]
                    }
                }
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, timeout=timeout)

        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()

        if response.status != 200:
            print(f"\nAPI错误: {response.status}")
            conn.close()
            return None, None

        full_content = ""
        buffer = b""
        tool_calls_accum = []

        while True:
            chunk = response.read(1024)
            if not chunk:
                break
            buffer += chunk

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    line = line.decode("utf-8").strip()
                except:
                    continue

                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        data = json.loads(line[6:])
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                            full_content += content
                        if "tool_calls" in delta:
                            tool_calls_accum.extend(delta["tool_calls"])
                    except:
                        continue

        conn.close()

        tool_calls = []
        if tool_calls_accum:
            merged = {}
            for tc in tool_calls_accum:
                idx = tc.get("index", 0)
                if idx not in merged:
                    merged[idx] = {
                        "id": tc.get("id", f"call_{idx}"),
                        "type": "function",
                        "function": {"name": "", "arguments": ""}
                    }
                if "function" in tc:
                    if "name" in tc["function"]:
                        merged[idx]["function"]["name"] = tc["function"]["name"]
                    if "arguments" in tc["function"]:
                        merged[idx]["function"]["arguments"] += tc["function"]["arguments"]
            tool_calls = list(merged.values())

        return full_content, tool_calls

    except Exception as e:
        print(f"\n连接错误: {e}")
        if 'conn' in locals():
            conn.close()
        return None, None

def main():
    print("=== LLM 聊天客户端（支持工具调用）===")
    print("按 Ctrl+C 退出聊天")
    print("=====================================")
    
    env = load_dotenv()
    api_key = env.get("API_KEY", "dummy")
    base_url = env.get("BASE_URL")
    model_name = env.get("MODEL_NAME")
    temperature = float(env.get("TEMPERATURE", "0.7"))
    max_tokens = int(env.get("MAX_TOKENS", 2048))

    if not base_url or not model_name:
        print("错误: 请在 .env 文件中设置 BASE_URL, MODEL_NAME")
        return

    print(f"模型: {model_name}")
    print(f"地址: {base_url}")
    chat_history = []

    try:
        while True:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            
            chat_history.append({"role": "user", "content": user_input})
            chat_history = chat_history[-10:]
            
            print("助手: ", end="", flush=True)
            assistant_response, tool_calls = call_llm_stream(
                api_key, base_url, model_name, temperature, max_tokens, chat_history
            )

            if tool_calls:
                for tool_call in tool_calls:
                    func = tool_call.get("function", {})
                    fn_name = func.get("name")
                    args_raw = func.get("arguments", "{}")

                    if not fn_name:
                        print("\n未识别工具")
                        continue

                    try:
                        args = json.loads(args_raw)
                    except:
                        print("\n工具参数错误")
                        continue

                    print(f"\n🔧 调用工具: {fn_name}")
                    if fn_name == "list_files":
                        res = list_files(args.get("directory"))
                    elif fn_name == "rename_file":
                        res = rename_file(args.get("directory"), args.get("old_name"), args.get("new_name"))
                    elif fn_name == "delete_file":
                        res = delete_file(args.get("directory"), args.get("file_name"))
                    elif fn_name == "create_file":
                        res = create_file(args.get("directory"), args.get("file_name"), args.get("content", ""))
                    elif fn_name == "read_file":
                        res = read_file(args.get("directory"), args.get("file_name"))
                    elif fn_name == "curl_request":
                        res = curl_request(args.get("url"), args.get("timeout", 30))
                    else:
                        res = "未知工具"

                    print(f"✅ {res}")
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", "call"),
                        "name": fn_name,
                        "content": res
                    })
                    print("\n助手: ", end="", flush=True)
                    call_llm_stream(api_key, base_url, model_name, temperature, max_tokens, chat_history)
            else:
                if assistant_response:
                    chat_history.append({"role": "assistant", "content": assistant_response})

            print("\n")

    except KeyboardInterrupt:
        print("\n退出聊天")

if __name__ == "__main__":
    main()