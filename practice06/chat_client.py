#!/usr/bin/env python3
"""
OpenAI 兼容协议 LLM 聊天客户端（支持流式输出、历史记录、链式工具调用）
practice06 增强版：实现链式工具调用，支持工具调用的顺序依赖和自主决策
"""

import os
import json
import http.client
import subprocess
import re
from urllib.parse import urlparse
import sys

def load_dotenv():
    """
    从项目根目录加载 .env 文件，自动定位根目录
    适配所有 practiceXX 子目录，不会跑到盘符根目录
    """
    # 1. 获取当前脚本的绝对路径
    script_path = os.path.abspath(sys.argv[0])
    # 2. 脚本所在目录（比如 practice06）
    script_dir = os.path.dirname(script_path)
    # 3. 项目根目录（往上跳一级，即 practice06 的父目录）
    project_root = os.path.dirname(script_dir)
    # 4. 拼接 .env 路径
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
    """读取项目目录下 .agents/skills 目录中的所有技能"""
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    skills_dir = os.path.join(project_root, ".agents", "skills")
    
    skills = []
    if not os.path.exists(skills_dir):
        print(f"警告: 技能目录 {skills_dir} 不存在")
        return skills
    
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue
        
        skill_file = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(skill_file):
            continue
        
        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if content.startswith("---"):
                end_index = content.find("---", 3)
                if end_index != -1:
                    front_matter = content[3:end_index].strip()
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
    """加载指定技能的 SKILL.md 文件正文内容"""
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    skill_path = os.path.join(project_root, ".agents", "skills", skill_name, "SKILL.md")
    
    if not os.path.exists(skill_path):
        return f"错误: 技能文件 {skill_path} 不存在"
    
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if content.startswith("---"):
            end_index = content.find("---", 3)
            if end_index != -1:
                return content[end_index+3:].strip()
        
        return content
    except Exception as e:
        return f"读取技能内容出错: {e}"

def anythingllm_query(message, timeout=60):
    """调用AnythingLLM的聊天API接口"""
    env = load_dotenv()
    api_key = env.get("ANYTHINGLLM_API_KEY")
    workspace_slug = env.get("ANYTHINGLLM_WORKSPACE_SLUG")
    
    if not api_key:
        return "错误: 请在 .env 文件中设置 ANYTHINGLLM_API_KEY"
    if not workspace_slug:
        return "错误: 请在 .env 文件中设置 ANYTHINGLLM_WORKSPACE_SLUG"
    
    api_url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    payload = {"message": message}
    
    cmd = [
        "curl", "-s", "-m", str(timeout),
        "-X", "POST",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload, ensure_ascii=False),
        api_url
    ]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = proc.communicate()
        
        if proc.returncode == 0:
            try:
                response = stdout.decode('utf-8').strip()
                try:
                    json_response = json.loads(response)
                    return json.dumps(json_response, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    return response
            except UnicodeDecodeError:
                return stdout.decode('gbk', errors='ignore').strip()
        else:
            error_msg = stderr.decode('utf-8', errors='ignore').strip()
            return f"curl 错误: {error_msg}"
    except Exception as e:
        return f"请求失败: {str(e)}"

def search_files_with_keyword(directory, keyword):
    """搜索指定目录下所有包含指定关键词的文件"""
    results = []
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if keyword in content:
                                lines = content.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines[:20], 1):
                                    if keyword in line:
                                        matching_lines.append(f"第{i}行: {line.strip()}")
                                results.append({
                                    "file": filepath,
                                    "matches": matching_lines[:5]
                                })
                    except Exception as e:
                        continue
        
        if not results:
            return f"在 {directory} 目录下未找到包含 '{keyword}' 的文件"
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"搜索失败: {str(e)}"

def fetch_webpage(url):
    """获取并解析网页完整内容（无额外依赖）"""
    cmd = ["curl", "-s", "-m", "30", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", url]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = proc.communicate()
        
        if proc.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='ignore').strip()
            return f"curl 错误: {error_msg}"
        
        html = stdout.decode('utf-8', errors='ignore')
        
        # 1. 提取标题
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "无标题"
        
        # 2. 提取正文内容（去除HTML标签和脚本）
        # 去除script/style标签
        html_clean = re.sub(r'<script.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html_clean = re.sub(r'<style.*?</style>', '', html_clean, flags=re.IGNORECASE | re.DOTALL)
        # 去除所有HTML标签
        text = re.sub(r'<[^>]+>', '', html_clean)
        # 去除多余空行和空格
        text = re.sub(r'\n+', '\n', text).strip()
        text = re.sub(r' +', ' ', text)
        
        # 3. 提取可能的发布日期
        date_match = re.search(r'发布时间[:：]\s*(\d{4}-\d{2}-\d{2})', text) or re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', text)
        publish_date = date_match.group(1) if date_match else "未找到"
        
        # 4. 格式化返回
        return f"""网页解析结果：
标题：{title}
发布日期：{publish_date}
URL：{url}
正文内容：
{text[:5000]}  # 限制长度，避免过长
"""
    
    except Exception as e:
        return f"请求失败: {str(e)}"

def read_file(filepath):
    """读取本地文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content.strip()
    except FileNotFoundError:
        return f"错误: 文件 {filepath} 不存在"
    except Exception as e:
        return f"读取文件失败: {str(e)}"

def save_to_file(content, filepath):
    """保存内容到文件"""
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"内容已成功保存到 {filepath}"
    except Exception as e:
        return f"保存失败: {str(e)}"

# ==================== 链式调用核心实现 ====================
class ChainedCallContext:
    """
    链式调用上下文管理器
    功能：
    1. 记录每一步工具调用的历史（工具名、参数、结果）
    2. 存储中间变量供后续步骤使用
    3. 控制最大迭代次数，防止无限循环
    """
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations  # 最大迭代次数
        self.iteration = 0                    # 当前迭代次数
        self.call_history = []                # 工具调用历史
        self.variables = {}                   # 中间变量存储
        self.user_request = ""                # 用户原始请求
    
    def reset(self):
        """重置上下文状态"""
        self.iteration = 0
        self.call_history = []
        self.variables = {}
        self.user_request = ""
    
    def set_user_request(self, request):
        """设置用户原始请求"""
        self.user_request = request
    
    def add_call(self, tool_name, arguments, result):
        """添加工具调用记录"""
        self.call_history.append({
            "step": self.iteration,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        })
        self.iteration += 1
    
    def get_history_summary(self):
        """获取工具调用历史摘要"""
        if not self.call_history:
            return "暂无工具调用记录"
        
        summary = "已执行的工具调用历史:\n"
        for call in self.call_history:
            summary += f"步骤 {call['step']}: 调用工具 '{call['tool_name']}'\n"
            summary += f"  参数: {json.dumps(call['arguments'], ensure_ascii=False)}\n"
            result_str = str(call['result'])[:200] + "..." if len(str(call['result'])) > 200 else str(call['result'])
            summary += f"  结果: {result_str}\n"
        
        return summary
    
    def is_max_iterations_reached(self):
        """检查是否达到最大迭代次数"""
        return self.iteration >= self.max_iterations
    
    def get_variable(self, name):
        """获取中间变量"""
        return self.variables.get(name)
    
    def set_variable(self, name, value):
        """设置中间变量"""
        self.variables[name] = value
    
    def get_context_info(self):
        """获取上下文信息（用于构建提示词）"""
        return {
            "user_request": self.user_request,
            "call_history": self.call_history,
            "variables": self.variables,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations
        }

def build_analysis_prompt(context):
    """
    构建分析提示词，指导LLM决策下一步操作
    包含：用户请求、历史记录、决策规则、输出格式
    """
    ctx_info = context.get_context_info()
    
    prompt = f"""
你是一个智能助手，需要根据用户的请求和已执行的工具调用历史，决定下一步操作。

## 用户原始请求
{ctx_info['user_request']}

## 已执行的工具调用历史
{context.get_history_summary()}

## 当前迭代次数
第 {ctx_info['iteration']} 次迭代（最大 {ctx_info['max_iterations']} 次）

## 可用工具列表
1. search_files_with_keyword(directory, keyword) - 搜索指定目录下包含关键词的文件
2. load_skill_content(skill_name) - 加载指定技能的内容
3. anythingllm_query(message) - 查询AnythingLLM文档仓库
4. fetch_webpage(url) - 获取网页内容
5. save_to_file(content, filepath) - 保存内容到文件
6. read_file(filepath) - 读取本地文件内容

## 决策规则
1. 分析用户请求和已执行的步骤，判断是否需要继续调用工具
2. 如果已获得足够信息可以直接回答用户，则标记任务完成
3. 如果需要更多信息或执行后续操作，则调用相应工具
4. 可以使用前一个工具的输出作为后一个工具的输入参数
5. 可以使用上下文变量（set_variable/get_variable）存储和传递中间结果

## 工具调用顺序依赖关系
- search_files_with_keyword → 可获取文件列表 → 可用于后续read_file分析
- fetch_webpage → 获取网页内容 → 可用于后续save_to_file保存
- load_skill_content → 获取技能规则 → 可用于指导后续操作
- read_file → 读取文件内容 → 可用于后续计算/分析/保存

## 输出格式要求（必须严格遵守JSON格式）
### 情况1：完成任务（可以直接回答用户）
{{"done": true, "answer": "最终回答内容"}}

### 情况2：继续调用工具
{{"done": false, "tool_call": {{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}}}

## 示例
用户请求："查找包含'def'的文件并总结内容"
第一次调用：
{{"done": false, "tool_call": {{"name": "search_files_with_keyword", "arguments": {{"directory": "practice05", "keyword": "def"}}}}}}
获取结果后，总结并完成：
{{"done": true, "answer": "找到X个文件，主要内容包括..."}}
"""
    
    return prompt.strip()

def extract_json_from_response(response):
    """
    从LLM响应中提取JSON部分
    处理markdown代码块、纯文本JSON等格式
    """
    if not response:
        return None
    
    # 匹配markdown代码块（```json ... ```）
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # 直接匹配JSON对象
    json_start = response.find('{')
    json_end = response.rfind('}')
    if json_start != -1 and json_end != -1 and json_start < json_end:
        return response[json_start:json_end+1]
    
    return response

def call_llm_non_stream(api_key, base_url, model, temperature, max_tokens, messages, timeout=30):
    """非流式调用LLM API（用于链式调用决策）"""
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = "/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        conn = http.client.HTTPSConnection(host, timeout=timeout) if parsed_url.scheme == "https" else http.client.HTTPConnection(host, timeout=timeout)
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        
        if response.status != 200:
            print(f"API错误: {response.status} {response.reason}")
            conn.close()
            return None
        
        data = response.read().decode('utf-8')
        conn.close()
        
        try:
            json_response = json.loads(data)
            if "choices" in json_response and json_response["choices"]:
                return json_response["choices"][0]["message"].get("content", "")
        except json.JSONDecodeError:
            return data
        
        return None
    except Exception as e:
        print(f"连接错误: {e}")
        return None

def execute_tool(tool_name, arguments):
    """执行指定工具调用"""
    try:
        if tool_name == "search_files_with_keyword":
            directory = arguments.get("directory", "")
            keyword = arguments.get("keyword", "")
            return search_files_with_keyword(directory, keyword)
        
        elif tool_name == "load_skill_content":
            skill_name = arguments.get("skill_name", "")
            return load_skill_content(skill_name)
        
        elif tool_name == "anythingllm_query":
            message = arguments.get("message", "")
            return anythingllm_query(message)
        
        elif tool_name == "fetch_webpage":
            url = arguments.get("url", "")
            return fetch_webpage(url)
        
        elif tool_name == "save_to_file":
            content = arguments.get("content", "")
            filepath = arguments.get("filepath", "")
            return save_to_file(content, filepath)
        
        elif tool_name == "read_file":
            filepath = arguments.get("filepath", "")
            return read_file(filepath)
        
        else:
            return f"未知工具: {tool_name}"
    except Exception as e:
        return f"工具执行异常: {str(e)}"

def execute_chained_tool_call(user_request, api_key, base_url, model, temperature, max_tokens, max_iterations=10):
    """
    执行链式工具调用的完整流程
    核心逻辑：循环调用LLM决策→执行工具→更新上下文，直到任务完成或达到最大迭代次数
    """
    print(f"\n=== 开始链式工具调用 ===")
    print(f"用户请求: {user_request}")
    
    # 1. 初始化上下文
    context = ChainedCallContext(max_iterations=max_iterations)
    context.set_user_request(user_request)
    
    # 2. 初始化系统提示词和消息历史
    system_prompt = """
你是一个智能助手，擅长进行多步骤的链式工具调用。

## 链式调用核心规则
1. 工具调用可以形成链式依赖：前一个工具的输出可以作为后一个工具的输入
2. 根据中间结果自主决定下一步操作，无需用户干预
3. 每次调用后检查是否已获得足够信息回答用户，若足够则标记任务完成
4. 可以使用上下文变量（set_variable/get_variable）存储和传递中间结果

## 工具调用顺序依赖示例
- 搜索文件 → 读取文件 → 分析内容 → 保存结果
- 获取网页 → 总结内容 → 保存到文件
- 加载技能 → 根据技能规则执行后续操作

## 输出格式要求（必须严格遵守）
完成任务：{"done": true, "answer": "最终回答内容"}
继续调用：{"done": false, "tool_call": {"name": "工具名", "arguments": {"参数名": "参数值"}}}
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # 3. 循环执行链式调用
    while not context.is_max_iterations_reached():
        print(f"\n--- 第 {context.iteration + 1} 次迭代 ---")
        
        # 构建分析提示词（包含用户请求+历史记录+决策规则）
        analysis_prompt = build_analysis_prompt(context)
        messages.append({"role": "user", "content": analysis_prompt})
        
        # 调用LLM决策下一步操作
        print("调用LLM分析决策...")
        llm_response = call_llm_non_stream(api_key, base_url, model, temperature, max_tokens, messages)
        
        if llm_response is None:
            print("LLM响应为空，终止链式调用")
            break
        
        print(f"LLM响应: {llm_response[:200]}..." if len(llm_response) > 200 else f"LLM响应: {llm_response}")
        
        # 解析LLM响应（处理JSON格式）
        try:
            json_str = extract_json_from_response(llm_response)
            if not json_str:
                print("无法提取JSON响应")
                break
            
            decision = json.loads(json_str)
            
            # 情况1：任务完成，返回最终回答
            if decision.get("done"):
                answer = decision.get("answer", "任务已完成")
                print(f"\n✓ 任务完成，最终回答: {answer[:100]}..." if len(answer) > 100 else f"\n✓ 任务完成，最终回答: {answer}")
                return answer
            
            # 情况2：继续调用工具
            tool_call = decision.get("tool_call")
            if not tool_call:
                print("未找到工具调用指令")
                break
            
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})
            
            print(f"执行工具调用: {tool_name}({arguments})")
            
            # 执行工具并记录到上下文
            result = execute_tool(tool_name, arguments)
            print(f"工具执行结果: {str(result)[:200]}..." if len(str(result)) > 200 else f"工具执行结果: {result}")
            
            context.add_call(tool_name, arguments, result)
            
            # 将工具调用结果添加到消息历史
            messages.append({
                "role": "assistant",
                "content": f"已调用工具 {tool_name}，结果: {str(result)[:100]}"
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            break
        except Exception as e:
            print(f"执行工具调用时出错: {e}")
            break
    
    # 达到最大迭代次数
    if context.is_max_iterations_reached():
        print(f"\n警告: 已达到最大迭代次数 {max_iterations}，终止链式调用")
    
    return f"链式调用结束，已执行 {context.iteration} 步操作。历史记录:\n{context.get_history_summary()}"

# ==================== 测试用例 ====================
def run_test_cases():
    """运行链式工具调用测试用例"""
    env = load_dotenv()
    api_key = env.get("API_KEY", "dummy")
    base_url = env.get("BASE_URL", "http://localhost:1234/v1")
    model_name = env.get("MODEL_NAME", "Qwen3.5-4b")
    temperature = float(env.get("TEMPERATURE", "0.7"))
    max_tokens = int(env.get("MAX_TOKENS", 2000))
    
    print("=== 运行链式工具调用测试用例 ===")
    
    # 测试1：文件搜索链式调用
    print("\n" + "="*50)
    print("测试1：文件搜索链式调用")
    print("="*50)
    test1_request = "请查找practice05目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
    execute_chained_tool_call(test1_request, api_key, base_url, model_name, temperature, max_tokens)
    
    # 测试2：技能查询链式调用
    print("\n" + "="*50)
    print("测试2：技能查询链式调用")
    print("="*50)
    test2_request = "我想了解notice技能的详细规则"
    execute_chained_tool_call(test2_request, api_key, base_url, model_name, temperature, max_tokens)
    
    # 测试3：网页处理链式调用
    print("\n" + "="*50)
    print("测试3：网页处理链式调用")
    print("="*50)
    test3_request = "访问https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 并总结页面内容，保存到practice06/summary.txt"
    execute_chained_tool_call(test3_request, api_key, base_url, model_name, temperature, max_tokens)
    
    print("\n=== 所有测试用例执行完成 ===")

# ==================== 主函数 ====================
def main():
    import sys
    print("=== LLM 聊天客户端（practice06 链式工具调用增强版）===")
    print("支持功能：流式输出、历史记录、链式工具调用（自主决策多步骤操作）")
    print("使用说明：")
    print("  - 直接运行：交互式聊天")
    print("  - python chat_client.py test：运行测试模式")
    print("  - python chat_client.py chain：运行链式调用测试用例")
    print("  - 按 Ctrl+C 退出")
    print("====================================")
    
    env = load_dotenv()
    api_key = env.get("API_KEY", "dummy")
    base_url = env.get("BASE_URL")
    model_name = env.get("MODEL_NAME")
    
    if not base_url or not model_name:
        print("错误: 请在 .env 文件中设置 BASE_URL, MODEL_NAME")
        return
    
    try:
        if "test" in sys.argv:
            # 测试模式
            user_input = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "你好"
            skills = list_available_skills()
            skills_json = json.dumps({"skills": skills}, ensure_ascii=False)
            
            chat_history = [
                {
                    "role": "system",
                    "content": f"你是智能助手，支持链式工具调用。可用技能列表:\n{skills_json}"
                },
                {"role": "user", "content": user_input}
            ]
            
            print(f"你: {user_input}")
            print("助手: 暂不支持流式链式调用，请使用 chain 参数运行测试用例")
        
        elif "chain" in sys.argv:
            # 运行链式调用测试用例
            run_test_cases()
        
        else:
            # 交互式聊天
            while True:
                user_input = input("\n你: ").strip()
                if not user_input:
                    continue
                
                # 对包含多步骤的请求，自动触发链式调用
                if any(keyword in user_input for keyword in ["查找", "总结", "访问", "保存", "了解", "读取", "def", "技能"]):
                    temperature = float(env.get("TEMPERATURE", "0.7"))
                    max_tokens = int(env.get("MAX_TOKENS", 2000))
                    result = execute_chained_tool_call(
                        user_input, api_key, base_url, model_name, temperature, max_tokens
                    )
                    print(f"\n最终结果: {result}")
                else:
                    print("助手: 请输入需要多步骤完成的请求（如'查找文件并总结'）以触发链式调用")
    
    except KeyboardInterrupt:
        print("\n\n退出聊天...")

if __name__ == "__main__":
    main()