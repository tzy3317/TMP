#!/usr/bin/env python3
"""
OpenAI 兼容协议 LLM 聊天客户端（支持工具调用、聊天记录总结和关键信息提取）
功能：
1. 当聊天超过5轮或上下文超过3k时，主动触发聊天记录总结
2. 每五次聊天提取一次关键信息，按照5W规则记录到本地文件
3. 支持搜索聊天历史功能
"""

import os
import json
import http.client
from urllib.parse import urlparse
from datetime import datetime

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
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = proc.communicate()
        
        if proc.returncode == 0:
            try:
                return stdout.decode('utf-8').strip()
            except UnicodeDecodeError:
                return stdout.decode('gbk', errors='ignore').strip()
        else:
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
            },
            {
                "type": "function",
                "function": {
                    "name": "search_chat_history",
                    "description": "搜索聊天历史记录",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词或问题"}
                        },
                        "required": ["query"]
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

def calculate_context_length(messages):
    """计算聊天上下文的长度"""
    total_length = 0
    for message in messages:
        if "content" in message:
            total_length += len(message["content"])
    return total_length

def summarize_chat_history(api_key, base_url, model, temperature, max_tokens, chat_history):
    """总结聊天历史记录"""
    print("\n📝 正在总结聊天历史...")
    
    total_messages = len(chat_history)
    if total_messages <= 2:
        print("✅ 无需总结")
        return chat_history
    
    compress_count = int(total_messages * 0.7)
    keep_count = total_messages - compress_count
    
    compress_messages = chat_history[:compress_count]
    keep_messages = chat_history[compress_count:]
    
    summary_prompt = "请总结以下聊天内容，保持关键信息，忽略不重要的细节：\n\n"
    for msg in compress_messages:
        role = "用户" if msg["role"] == "user" else "助手"
        if "content" in msg:
            summary_prompt += f"{role}: {msg['content']}\n"
    
    summary_messages = [
        {"role": "system", "content": "你是一个聊天记录总结助手，需要简洁明了地总结聊天内容"},
        {"role": "user", "content": summary_prompt}
    ]
    
    print("助手: ", end="", flush=True)
    summary, _ = call_llm_stream(api_key, base_url, model, temperature, max_tokens, summary_messages)
    
    new_chat_history = []
    if summary:
        new_chat_history.append({
            "role": "assistant",
            "content": f"[聊天历史总结]\n{summary}"
        })
    new_chat_history.extend(keep_messages)
    
    print("\n✅ 聊天历史总结完成")
    return new_chat_history

def extract_key_info(api_key, base_url, model, temperature, max_tokens, chat_history):
    """提取聊天关键信息并记录到文件"""
    print("\n🔍 正在提取关键信息...")
    
    keyinfo_prompt = "请从以下聊天内容中提取关键信息，按照5W规则（谁Who、做了什么事What、什么时候When（可选）、在何处Where（可选）、为什么要做这个事Why（可选））进行提取，每条信息单独一行：\n\n"
    for msg in chat_history:
        role = "用户" if msg["role"] == "user" else "助手"
        if "content" in msg:
            keyinfo_prompt += f"{role}: {msg['content']}\n"
    
    keyinfo_messages = [
        {"role": "system", "content": "你是一个关键信息提取助手，需要按照5W规则从聊天内容中提取关键信息"},
        {"role": "user", "content": keyinfo_prompt}
    ]
    
    print("助手: ", end="", flush=True)
    keyinfo, _ = call_llm_stream(api_key, base_url, model, temperature, max_tokens, keyinfo_messages)
    
    if keyinfo:
        log_dir = "D:\\chat-log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, "log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== {timestamp} ===\n")
            f.write(keyinfo)
            f.write("\n")
        
        print(f"\n✅ 关键信息已记录到 {log_file}")
    else:
        print("\n❌ 提取关键信息失败")

def get_full_chat_log():
    """读取完整的聊天历史日志"""
    log_file = "D:\\chat-log\\log.txt"
    if not os.path.exists(log_file):
        return "暂无聊天历史记录"
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "读取历史记录失败"

def main():
    print("=== LLM 聊天客户端（支持工具调用、聊天记录总结和关键信息提取）===")
    print("按 Ctrl+C 退出聊天")
    print("使用 /search 开头的消息可以搜索聊天历史")
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
    chat_count = 0

    try:
        while True:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            
            # 搜索功能：直接把完整日志给模型去理解
            if user_input.startswith("/search"):
                chat_count += 1
                query = user_input[8:].strip()
                if not query:
                    print("助手: 请输入要查询的内容")
                    continue

                full_log = get_full_chat_log()
                prompt = f"""
你是智能问答助手，请根据下面的【聊天历史关键信息】回答用户问题。
只需要根据记录回答，不要编造信息。

【聊天历史关键信息】
{full_log}

【用户问题】
{query}

请直接回答：
""".strip()
                
                messages = [
                    {"role": "system", "content": "你根据聊天历史回答问题，简洁准确"},
                    {"role": "user", "content": prompt}
                ]
                
                print("助手: ", end="", flush=True)
                resp, _ = call_llm_stream(api_key, base_url, model_name, temperature, max_tokens, messages)
                if resp:
                    chat_history.append({"role": "user", "content": user_input})
                    chat_history.append({"role": "assistant", "content": resp})
                print("\n")
                continue

            # 正常对话
            chat_count += 1
            chat_history.append({"role": "user", "content": user_input})
            print("助手: ", end="", flush=True)
            assistant_response, tool_calls = call_llm_stream(
                api_key, base_url, model_name, temperature, max_tokens, chat_history
            )

            # 工具调用
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
                        print("\n工具参数解析失败")
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
                    elif fn_name == "search_chat_history":
                        res = get_full_chat_log()
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
                    final_response, _ = call_llm_stream(api_key, base_url, model_name, temperature, max_tokens, chat_history)
                    if final_response:
                        assistant_response = final_response
            else:
                if assistant_response:
                    chat_history.append({"role": "assistant", "content": assistant_response})

            # 每5轮提取关键信息
            if chat_count % 5 == 0:
                extract_key_info(api_key, base_url, model_name, temperature, max_tokens, chat_history)

            # 超过长度自动总结
            context_len = calculate_context_length(chat_history)
            if len(chat_history) > 10 or context_len > 3000:
                chat_history = summarize_chat_history(api_key, base_url, model_name, temperature, max_tokens, chat_history)

            print("\n")

    except KeyboardInterrupt:
        print("\n退出聊天")

if __name__ == "__main__":
    main()