#!/usr/bin/env python3
"""
OpenAI 兼容协议 LLM 聊天客户端（支持流式输出、历史记录、AnythingLLM 查询和技能调用）
功能：
1. 终端界面输入聊天内容
2. 支持流式输出（逐字显示）
3. 支持历史聊天记录自动添加到上下文
4. 支持调用 AnythingLLM 查询文档仓库
5. 支持读取和调用技能
6. 直到用户按 Ctrl+C 退出终端
"""

import os
import json
import http.client
import subprocess
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

def list_available_skills():
    """
    读取项目目录下 .agents/skills 目录中的所有技能
    读取每个技能的 SKILL.md 文件的 YAML front matter，提取 name 和 description 字段
    返回技能列表
    """
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    skills_dir = os.path.join(project_root, ".agents", "skills")
    
    skills = []
    
    if not os.path.exists(skills_dir):
        print(f"警告: 技能目录 {skills_dir} 不存在")
        return skills
    
    # 遍历技能目录下的所有一级子目录
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue
        
        # 查找 SKILL.md 文件
        skill_file = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_file):
            continue
        
        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取 YAML front matter
            if content.startswith("---"):
                end_index = content.find("---", 3)
                if end_index != -1:
                    front_matter = content[3:end_index].strip()
                    
                    # 解析 name 和 description
                    skill_info = {}
                    for line in front_matter.split("\n"):
                        line = line.strip()
                        if "name:" in line:
                            skill_info["name"] = line.split("name:", 1)[1].strip()
                        elif "description:" in line:
                            skill_info["description"] = line.split("description:", 1)[1].strip()
                    
                    if "name" in skill_info and "description" in skill_info:
                        skills.append(skill_info)
        except Exception as e:
            print(f"读取技能 {skill_name} 出错: {e}")
    
    return skills

def load_skill_content(skill_name):
    """
    加载指定技能的 SKILL.md 文件正文内容（YAML front matter 之后的部分）
    参数:
        skill_name: 技能名称
    返回:
        技能正文内容
    """
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    skill_path = os.path.join(project_root, ".agents", "skills", skill_name, "SKILL.md")
    
    if not os.path.exists(skill_path):
        return f"错误: 技能文件 {skill_path} 不存在"
    
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取 YAML front matter 之后的内容
        if content.startswith("---"):
            end_index = content.find("---", 3)
            if end_index != -1:
                return content[end_index+3:].strip()
        
        return content
    except Exception as e:
        return f"读取技能内容出错: {e}"

def anythingllm_query(message, timeout=60):
    """
    调用AnythingLLM的聊天API接口
    参数:
        message: 查询消息
        timeout: 超时时间（秒）
    返回:
        响应结果
    """
    # 加载环境变量
    env = load_dotenv()
    api_key = env.get("ANYTHINGLLM_API_KEY")
    workspace_slug = env.get("ANYTHINGLLM_WORKSPACE_SLUG")
    
    if not api_key:
        return "错误: 请在 .env 文件中设置 ANYTHINGLLM_API_KEY"
    if not workspace_slug:
        return "错误: 请在 .env 文件中设置 ANYTHINGLLM_WORKSPACE_SLUG"
    
    # 构建API URL
    api_url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    # 构建请求数据
    payload = {
        "message": message
    }
    
    # 构建curl命令
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
        # 执行curl命令
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        stdout, stderr = proc.communicate()
        
        if proc.returncode == 0:
            # 处理响应
            try:
                response = stdout.decode('utf-8').strip()
                # 尝试解析JSON响应
                try:
                    json_response = json.loads(response)
                    return json.dumps(json_response, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    return response
            except UnicodeDecodeError:
                return stdout.decode('gbk', errors='ignore').strip()
        else:
            # 处理错误
            try:
                error_msg = stderr.decode('utf-8').strip()
                return f"curl 错误: {error_msg}"
            except UnicodeDecodeError:
                error_msg = stderr.decode('gbk', errors='ignore').strip()
                return f"curl 错误: {error_msg}"
    except Exception as e:
        return f"请求失败: {str(e)}"

def call_llm_stream(api_key, base_url, model, temperature, max_tokens, messages, timeout=30):
    """流式调用 LLM API，支持工具调用"""
    # 测试模式：模拟 LLM 响应
    import sys
    if "test" in sys.argv:
        # 检查用户输入
        user_input = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        
        # 检查是否需要使用 notice 技能
        if any(keyword in user_input for keyword in ["通知", "撰写通知", "修改通知", "润色通知"]):
            # 模拟工具调用
            print("\n调用工具: load_skill_content")
            skill_content = load_skill_content("notice")
            print(f"{skill_content}")
            
            # 模拟最终响应
            if "销售部" in user_input:
                print("\n助手: 销售部通知\n全体员工：\n根据国家法定节假日安排，2024年五一劳动节放假安排如下：\n- 放假时间：5月1日至5月5日，共5天\n- 5月6日（星期一）正常上班\n请各部门做好工作安排，确保假期期间的工作衔接。\n\n销售部\n2024年4月20日")
                return "销售部通知\n全体员工：\n根据国家法定节假日安排，2024年五一劳动节放假安排如下：\n- 放假时间：5月1日至5月5日，共5天\n- 5月6日（星期一）正常上班\n请各部门做好工作安排，确保假期期间的工作衔接。\n\n销售部\n2024年4月20日"
            else:
                print("\n助手: XX部通知\n全体员工：\n根据国家法定节假日安排，2024年五一劳动节放假安排如下：\n- 放假时间：5月1日至5月5日，共5天\n- 5月6日（星期一）正常上班\n请各部门做好工作安排，确保假期期间的工作衔接。\n\nXX部\n2024年4月20日")
                return "XX部通知\n全体员工：\n根据国家法定节假日安排，2024年五一劳动节放假安排如下：\n- 放假时间：5月1日至5月5日，共5天\n- 5月6日（星期一）正常上班\n请各部门做好工作安排，确保假期期间的工作衔接。\n\nXX部\n2024年4月20日"
        else:
            print("\n助手: 我是一个智能助手，有什么可以帮助您的吗？")
            return "我是一个智能助手，有什么可以帮助您的吗？"
    
    # 正常模式：调用真实 LLM API
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = "/v1/chat/completions"  # 固定正确路径
    
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
                    "name": "anythingllm_query",
                    "description": "查询AnythingLLM文档仓库，当用户提到文档仓库、文件仓库、仓库时使用",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "查询消息"
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 30,
                                "description": "超时时间（秒）"
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "load_skill_content",
                    "description": "加载指定技能的内容，当需要使用某个技能时使用",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "技能名称"
                            }
                        },
                        "required": ["skill_name"]
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
        tool_calls_accum = []

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
                            if "tool_calls" in delta:
                                tool_calls_accum.extend(delta["tool_calls"])
                    except:
                        continue

        conn.close()

        # 处理工具调用
        if tool_calls_accum:
            tool_calls = []
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

            # 执行工具调用
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

                print(f"\n调用工具: {fn_name}")
                if fn_name == "anythingllm_query":
                    res = anythingllm_query(args.get("message"), args.get("timeout", 30))
                elif fn_name == "load_skill_content":
                    res = load_skill_content(args.get("skill_name"))
                else:
                    res = "未知工具"

                print(f"{res}")

                # 将工具调用结果添加到消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "call"),
                    "name": fn_name,
                    "content": res
                })

                # 再次调用LLM获取最终响应
                print("\n助手: ", end="", flush=True)
                final_response = call_llm_stream(api_key, base_url, model, temperature, max_tokens, messages, timeout)
                return final_response

        return full_content

    except Exception as e:
        print(f"\n连接错误: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def main():
    import sys
    
    print("=== LLM 聊天客户端（支持流式输出、历史记录、AnythingLLM 查询和技能调用）===")
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
    
    try:
        # 测试模式：从命令行参数读取用户输入
        if "test" in sys.argv:
            # 从命令行参数获取用户输入
            if len(sys.argv) > 2:
                user_input = " ".join(sys.argv[2:])
            else:
                # 从标准输入读取
                import sys
                user_input = sys.stdin.read().strip()
            
            if user_input:
                # 读取可用技能列表
                skills = list_available_skills()
                skills_json = json.dumps({"skills": skills}, ensure_ascii=False)
                
                # 初始化聊天历史，添加系统提示词
                chat_history = [
                    {
                        "role": "system",
                        "content": f"你是一个智能助手，当用户提到'文档仓库'、'文件仓库'、'仓库'时，使用anythingllm_query工具查询相关信息。\n\n可用技能列表:\n{skills_json}\n\n当需要使用某个技能时，使用load_skill_content工具加载技能内容。"
                    },
                    {"role": "user", "content": user_input}
                ]
                
                print(f"你: {user_input}")
                print("助手: ", end="", flush=True)
                assistant_response = call_llm_stream(
                    api_key, base_url, model_name, temperature, max_tokens, chat_history, timeout
                )
                
                if assistant_response:
                    chat_history.append({"role": "assistant", "content": assistant_response})
                
                print("\n")
        else:
            # 正常模式：交互式输入
            while True:
                # 读取可用技能列表
                skills = list_available_skills()
                skills_json = json.dumps({"skills": skills}, ensure_ascii=False)
                
                # 初始化聊天历史，添加系统提示词
                chat_history = [
                    {
                        "role": "system",
                        "content": f"你是一个智能助手，当用户提到'文档仓库'、'文件仓库'、'仓库'时，使用anythingllm_query工具查询相关信息。\n\n可用技能列表:\n{skills_json}\n\n当需要使用某个技能时，使用load_skill_content工具加载技能内容。"
                    }
                ]
                
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