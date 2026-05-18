# AI 智能体开发学习项目

## 项目简介

本项目是一个基于 Python 的 AI 智能体开发学习框架，旨在帮助开发者理解如何使用标准库与 LLM（大语言模型）进行交互。项目包含了基本的环境配置、API 调用和统计功能，为学习 AI 智能体开发提供了基础示例。

## 项目结构

```
├── .env               # 环境配置文件（用户创建）
├── .env.example       # 环境配置模板
├── practice01/        # 练习目录
│   ├── call_llm.py    # LLM API 调用脚本
│   ├── llm_client.py  # LLM 客户端（模拟实现）
│   └── chat_client.py # LLM 聊天客户端（支持流式输出和历史记录）
├── practice02/        # 练习目录（支持工具调用）
│   └── chat_client_with_tools.py # LLM 聊天客户端（支持工具调用和curl网络访问）
├── practice03/        # 练习目录（支持聊天记录总结和关键信息提取）
│   ├── chat_client_with_summary.py # LLM 聊天客户端（支持工具调用和聊天记录总结）
│   └── chat_client_with_keyinfo.py # LLM 聊天客户端（支持工具调用、聊天记录总结和关键信息提取）
├── practice04/        # 练习目录（支持 AnythingLLM 查询）
│   ├── anythingllm_client.py # AnythingLLM 查询客户端
│   ├── chat_client_with_keyinfo.py # 复制自 practice03
│   └── chat_client_with_summary.py # 复制自 practice03
├── practice05/        # 练习目录（支持技能调用）
│   └── chat_client.py # LLM 聊天客户端（支持技能调用）
├── practice06/        # 练习目录（支持链式工具调用）
│   └── chat_client.py # LLM 聊天客户端（支持链式工具调用）
├── practice07/        # 练习目录（测试输出目录）
│   └── summary.txt    # 网页内容总结示例文件
├── tool_chat_client.py # LLM 聊天客户端（支持工具调用和curl网络访问）
├── venv/              # 虚拟环境
└── requirements.txt   # 依赖包配置
```

## 代码功能说明

### 1. practice01/call_llm.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 使用标准库 `http.client` 调用 OpenAI 兼容协议的 LLM API
- 统计 token 消耗、请求时间和 token 处理速度
- 输出响应内容和详细的统计信息

**教学目标**：
- 学习如何使用标准库进行 HTTP 请求
- 了解 OpenAI 兼容协议的 API 调用格式
- 掌握 token 消耗统计和性能分析方法
- 学习错误处理和异常捕获

**核心功能**：
- `load_env()`: 读取并解析 .env 文件
- `call_llm()`: 发送 API 请求并处理响应
- `main()`: 主函数，协调各个功能模块

### 2. practice01/llm_client.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 模拟 LLM API 调用（不实际发送网络请求）
- 统计 token 消耗、请求时间和 token 处理速度
- 输出详细的统计信息

**教学目标**：
- 学习如何加载和解析配置文件
- 了解 LLM API 调用的基本流程
- 掌握性能统计和分析方法
- 学习模拟测试的方法

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `main()`: 主函数，模拟 API 调用并输出统计信息

### 3. practice01/chat_client.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持流式输出（逐字显示）
- 自动保存历史聊天记录到上下文
- 支持调用 AnythingLLM 查询文档仓库
- 当用户提到"文档仓库”、“文件仓库”、“仓库”时触发 anythingllm_query 工具
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现流式 API 调用
- 了解如何处理 SSE（Server-Sent Events）格式的响应
- 掌握聊天历史管理和上下文维护
- 学习工具调用功能的实现
- 了解如何集成外部 API（如 AnythingLLM）
- 学习终端交互和异常处理

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `anythingllm_query()`: 调用 AnythingLLM 的聊天 API 接口
- `call_llm_stream()`: 流式调用 LLM API（支持工具调用）
- `main()`: 主函数，处理用户输入、工具调用和聊天循环

### 4. practice02/chat_client_with_tools.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持工具调用功能
- 支持curl网络访问功能
- 支持流式输出（逐字显示）
- 自动保存历史聊天记录到上下文
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现工具调用功能
- 了解如何通过curl访问网页并获取内容
- 掌握工具调用的参数处理和结果返回
- 学习错误处理和异常捕获

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `list_files()`: 列出目录下的文件
- `rename_file()`: 重命名文件
- `delete_file()`: 删除文件
- `create_file()`: 创建文件
- `read_file()`: 读取文件内容
- `curl_request()`: 通过curl访问网页并返回内容
- `call_llm_stream()`: 流式调用 LLM API（支持工具调用）
- `main()`: 主函数，处理用户输入、工具调用和聊天循环

### 5. tool_chat_client.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持工具调用功能
- 支持curl网络访问功能
- 支持流式输出（逐字显示）
- 自动保存历史聊天记录到上下文
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现工具调用功能
- 了解如何通过curl访问网页并获取内容
- 掌握工具调用的参数处理和结果返回
- 学习错误处理和异常捕获

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `list_files()`: 列出目录下的文件
- `rename_file()`: 重命名文件
- `delete_file()`: 删除文件
- `create_file()`: 创建文件
- `read_file()`: 读取文件内容
- `curl_request()`: 通过curl访问网页并返回内容
- `call_llm_stream()`: 流式调用 LLM API（支持工具调用）
- `main()`: 主函数，处理用户输入、工具调用和聊天循环

### 6. practice03/chat_client_with_summary.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持工具调用功能
- 支持curl网络访问功能
- 支持流式输出（逐字显示）
- 自动保存历史聊天记录到上下文
- 当聊天超过5轮或上下文超过3k时，主动触发聊天记录总结
- 对前70%左右的内容进行压缩，最后30%左右的内容保留原文
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现聊天记录总结功能
- 了解如何管理和压缩聊天上下文
- 掌握触发条件的设置和判断
- 学习如何使用LLM进行内容总结

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `list_files()`: 列出目录下的文件
- `rename_file()`: 重命名文件
- `delete_file()`: 删除文件
- `create_file()`: 创建文件
- `read_file()`: 读取文件内容
- `curl_request()`: 通过curl访问网页并返回内容
- `call_llm_stream()`: 流式调用 LLM API（支持工具调用）
- `calculate_context_length()`: 计算聊天上下文的长度
- `summarize_chat_history()`: 总结聊天历史记录
- `main()`: 主函数，处理用户输入、工具调用、聊天记录总结和聊天循环

### 7. practice03/chat_client_with_keyinfo.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持工具调用功能
- 支持curl网络访问功能
- 支持流式输出（逐字显示）
- 自动保存历史聊天记录到上下文
- 当聊天超过5轮或上下文超过3k时，主动触发聊天记录总结
- 每五次聊天提取一次关键信息，按照5W规则记录到本地文件
- 支持搜索聊天历史功能
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现关键信息提取功能
- 了解如何按照5W规则组织信息
- 掌握文件操作和目录创建
- 学习如何实现聊天历史搜索功能

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `list_files()`: 列出目录下的文件
- `rename_file()`: 重命名文件
- `delete_file()`: 删除文件
- `create_file()`: 创建文件
- `read_file()`: 读取文件内容
- `curl_request()`: 通过curl访问网页并返回内容
- `call_llm_stream()`: 流式调用 LLM API（支持工具调用）
- `calculate_context_length()`: 计算聊天上下文的长度
- `summarize_chat_history()`: 总结聊天历史记录
- `extract_key_info()`: 提取聊天关键信息并记录到文件
- `search_chat_history()`: 搜索聊天历史记录
- `main()`: 主函数，处理用户输入、工具调用、关键信息提取、聊天记录总结和聊天循环

### 8. practice04/anythingllm_client.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 使用 subprocess 模块调用curl命令访问 AnythingLLM 的聊天 API 接口
- 支持中文编码处理
- 使用 API 密钥进行认证
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何使用 subprocess 模块调用外部命令
- 了解如何处理 API 认证和请求构建
- 掌握中文编码处理
- 学习如何集成外部 API（如 AnythingLLM）
- 学习错误处理和异常捕获

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `anythingllm_query()`: 调用 AnythingLLM 的聊天 API 接口
- `main()`: 主函数，处理用户输入和聊天循环

### 9. practice05/chat_client.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持流式输出（逐字显示）
- 自动保存历史聊天记录到上下文
- 支持调用 AnythingLLM 查询文档仓库
- 支持读取和调用技能
- 每次用户提交输入时，自动读取项目目录下 `.agents/skills` 目录中的所有技能
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现技能加载和调用功能
- 了解如何读取和解析 YAML front matter
- 掌握如何动态生成系统提示词
- 学习如何在工具调用中集成技能内容
- 了解如何组织和管理技能目录结构

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `list_available_skills()`: 读取项目目录下 .agents/skills 目录中的所有技能，提取 name 和 description 字段
- `load_skill_content()`: 加载指定技能的 SKILL.md 文件正文内容（YAML front matter 之后的部分）
- `anythingllm_query()`: 调用 AnythingLLM 的聊天 API 接口
- `call_llm_stream()`: 流式调用 LLM API（支持工具调用）
- `main()`: 主函数，处理用户输入、技能加载和聊天循环

### 10. practice06/chat_client.py

**功能用途**：
- 读取项目根目录的 `.env` 配置文件
- 提供终端界面进行聊天交互
- 支持流式输出（逐字显示）
- 支持链式工具调用（Chained Tool Calls）
- 自动保存历史聊天记录到上下文
- 支持读取和调用技能
- 支持文件搜索、网页获取、文件保存等工具
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现链式工具调用功能
- 了解如何在多个工具调用之间传递数据和状态
- 掌握上下文管理器的设计和实现
- 学习如何构建分析提示词引导 LLM 决策
- 了解如何处理 JSON 格式的 LLM 响应
- 掌握防止无限循环的方法

**核心功能**：
- `ChainedCallContext`: 链式调用上下文管理器，记录每一步的调用和结果，存储中间变量
- `build_analysis_prompt()`: 构建分析提示词，包含用户请求、已执行步骤历史和决策规则
- `execute_chained_tool_call()`: 执行链式工具调用的完整流程
- `execute_tool()`: 执行指定的工具
- `extract_json_from_response()`: 从 LLM 响应中提取 JSON 部分
- `search_files_with_keyword()`: 搜索指定目录下包含关键词的文件
- `fetch_webpage()`: 获取网页内容
- `save_to_file()`: 保存内容到文件
- `call_llm_non_stream()`: 非流式调用 LLM API，用于链式工具调用决策
- `run_test_cases()`: 运行链式工具调用测试用例
- `main()`: 主函数，处理用户输入、链式工具调用和聊天循环

**链式调用输出格式**：
- 完成任务：`{"done": true, "answer": "最终回答内容"}`
- 继续调用工具：`{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}`

**支持的工具列表**：
1. `search_files_with_keyword(directory, keyword)` - 搜索指定目录下包含关键词的文件
2. `load_skill_content(skill_name)` - 加载指定技能的内容
3. `anythingllm_query(message)` - 查询 AnythingLLM 文档仓库
4. `fetch_webpage(url)` - 获取网页内容
5. `save_to_file(content, filepath)` - 保存内容到文件
6. `read_file(filepath)` - 读取本地文件内容

## 环境配置

1. **创建虚拟环境**：
   ```powershell
   python -m venv venv
   ```

2. **激活虚拟环境**：
   ```powershell
   venv\Scripts\activate
   ```

3. **安装依赖**：
   ```powershell
   pip install -r requirements.txt
   ```

4. **配置环境变量**：
   ```powershell
   copy .env.example .env
   ```
   然后编辑 `.env` 文件，填入你的 API 密钥和其他配置。

## 使用方法

### 运行 call_llm.py

```powershell
cd practice01
python call_llm.py
```

**功能**：调用真实的 LLM API，返回响应内容和统计信息。

### 运行 llm_client.py

```powershell
cd practice01
python llm_client.py
```

**功能**：模拟 LLM API 调用，输出统计信息。

### 运行 chat_client.py

```powershell
cd practice01
python chat_client.py
```

**功能**：启动交互式聊天客户端，支持流式输出、历史记录和 AnythingLLM 查询。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 当提到"文档仓库”、“文件仓库”、“仓库”时，助手会自动调用 AnythingLLM 查询相关信息
4. 继续输入新的问题
5. 按 Ctrl+C 退出聊天

### 运行 practice02/chat_client_with_tools.py

```powershell
cd practice02
python chat_client_with_tools.py
```

**功能**：启动支持工具调用的交互式聊天客户端，包括文件操作和curl网络访问功能。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 如果助手需要调用工具，会自动执行并显示结果
4. 继续输入新的问题
5. 按 Ctrl+C 退出聊天

### 运行 tool_chat_client.py

```powershell
python tool_chat_client.py
```

**功能**：启动支持工具调用的交互式聊天客户端，包括文件操作和curl网络访问功能。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 如果助手需要调用工具，会自动执行并显示结果
4. 继续输入新的问题
5. 按 Ctrl+C 退出聊天

### 运行 practice03/chat_client_with_summary.py

```powershell
cd practice03
python chat_client_with_summary.py
```

**功能**：启动支持工具调用和聊天记录总结的交互式聊天客户端。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 如果助手需要调用工具，会自动执行并显示结果
4. 当聊天超过5轮或上下文超过3k时，系统会自动触发聊天记录总结
5. 继续输入新的问题
6. 按 Ctrl+C 退出聊天

### 运行 practice03/chat_client_with_keyinfo.py

```powershell
cd practice03
python chat_client_with_keyinfo.py
```

**功能**：启动支持工具调用、聊天记录总结和关键信息提取的交互式聊天客户端。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 如果助手需要调用工具，会自动执行并显示结果
4. 当聊天超过5轮或上下文超过3k时，系统会自动触发聊天记录总结
5. 每五次聊天，系统会自动提取关键信息并按照5W规则记录到 D:\chat-log\log.txt 文件
6. 使用 /search 开头的消息可以搜索聊天历史
7. 按 Ctrl+C 退出聊天

### 运行 practice04/anythingllm_client.py

```powershell
cd practice04
python anythingllm_client.py
```

**功能**：启动 AnythingLLM 查询客户端，直接调用 AnythingLLM 的聊天 API 接口。

**使用方法**：
1. 输入你的查询消息
2. 等待响应结果（会显示 AnythingLLM 的返回内容）
3. 继续输入新的查询
4. 按 Ctrl+C 退出聊天

### 运行 practice05/chat_client.py

```powershell
cd practice05
python chat_client.py
```

**功能**：启动支持技能调用的交互式聊天客户端。

**使用方法**：
1. 输入你的问题或消息（如"请撰写一份关于五一节放假的通知"）
2. 等待助手的响应（流式输出）
3. 系统会自动读取 `.agents/skills` 目录中的所有技能，并在需要时调用相应的技能
4. 当需要使用某个技能时，助手会自动加载技能内容并遵照执行
5. 继续输入新的问题
6. 按 Ctrl+C 退出聊天

**测试示例**：
1. 测试场景1（不指定部门）：
   ```
   你: 请撰写一份关于五一节放假的通知
   助手: XX部通知
   全体员工：
   根据国家法定节假日安排，2024年五一劳动节放假安排如下：
   - 放假时间：5月1日至5月5日，共5天
   - 5月6日（星期一）正常上班
   请各部门做好工作安排，确保假期期间的工作衔接。
   
   XX部
   2024年4月20日
   ```

2. 测试场景2（指定销售部）：
   ```
   你: 我是销售部的，请撰写一份关于五一节放假的通知
   助手: 销售部通知
   全体员工：
   根据国家法定节假日安排，2024年五一劳动节放假安排如下：
   - 放假时间：5月1日至5月5日，共5天
   - 5月6日（星期一）正常上班
   请各部门做好工作安排，确保假期期间的工作衔接。
   
   销售部
   2024年4月20日
   ```

### 运行 practice06/chat_client.py

```powershell
cd practice06
python chat_client.py
```

**功能**：启动支持链式工具调用的交互式聊天客户端。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 如果需要链式工具调用，系统会自动执行多步操作
4. 继续输入新的问题
5. 按 Ctrl+C 退出聊天

**运行测试用例**：

```powershell
cd practice06
python chat_client.py chain
```

**测试用例说明**：

1. **测试1：文件搜索链式调用**
   - 用户请求："请查找practice05目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
   - 执行流程：调用 `search_files_with_keyword` 工具搜索文件，然后总结结果

2. **测试2：技能查询链式调用**
   - 用户请求："我想了解notice技能的详细规则"
   - 执行流程：调用 `load_skill_content` 工具加载技能内容

3. **测试3：网页处理链式调用**
   - 用户请求："访问 https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html 并总结页面内容，保存到practice07/summary.txt"
   - 执行流程：调用 `fetch_webpage` 获取网页内容 → 总结内容 → 调用 `save_to_file` 保存到文件

4. **测试4：文件读取和计算链式调用**
   - 用户请求："读取D:\tmp\practice06目录下的1.txt和2.txt文件，里面分别有两个整数，告诉我它们相加之和"
   - 执行流程：调用 `read_file` 读取1.txt → 调用 `read_file` 读取2.txt → 计算两数之和

**链式调用特性**：
- 支持前一个工具的输出作为后一个工具的输入参数
- LLM 可以根据中间结果自主决定下一步工具调用
- 设置最大迭代次数（默认10次）防止无限循环
- 支持 JSON 格式和 tool_calls 格式的响应解析
- 自动处理包含 markdown 代码块标记的响应

## 配置说明

### .env 文件配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| API_KEY | LLM API 密钥 | 无（必填） |
| BASE_URL | LLM API 基础 URL | https://api.openai.com/v1 |
| MODEL_NAME | 使用的模型名称 | gpt-3.5-turbo |
| MAX_TOKENS | 最大生成 token 数 | 2000 |
| TEMPERATURE | 生成温度参数 | 0.7 |
| TIMEOUT | 请求超时时间（秒） | 30 |
| ANYTHINGLLM_API_KEY | AnythingLLM API 密钥 | 无（使用 AnythingLLM 功能时必填） |
| ANYTHINGLLM_WORKSPACE_SLUG | AnythingLLM 工作区 slug | 无（使用 AnythingLLM 功能时必填） |

## 教学要点

1. **标准库使用**：学习如何使用 Python 标准库（如 `http.client`、`json`、`os`）进行网络请求和文件操作。

2. **API 调用**：了解如何构建和发送符合 OpenAI 兼容协议的 API 请求。

3. **配置管理**：学习如何使用 `.env` 文件管理环境变量和配置信息。

4. **性能分析**：掌握如何统计和分析 API 调用的性能指标（如 token 消耗、响应时间）。

5. **错误处理**：学习如何处理网络请求和 API 调用中可能出现的错误。

6. **模块化设计**：了解如何将代码组织成功能明确的模块和函数。

7. **流式输出**：学习如何实现流式 API 调用和处理 SSE 格式的响应。

8. **聊天历史管理**：掌握如何维护聊天上下文和管理历史记录。

9. **终端交互**：学习如何实现命令行交互式应用程序。

## 扩展建议

1. **添加更多模型支持**：扩展代码以支持不同的 LLM 模型。

2. **实现会话管理**：添加会话管理功能，支持多轮对话。

3. **添加缓存机制**：实现请求缓存，减少重复请求。

4. **添加异步支持**：使用 `asyncio` 实现异步 API 调用。

5. **添加更复杂的统计分析**：实现更详细的性能分析和报告生成。

## 注意事项

- 确保 `.env` 文件中的 API 密钥正确且有效。
- 注意 API 调用的频率限制，避免超出配额。
- 对于生产环境，建议使用更安全的方式管理 API 密钥。
- 本项目仅用于学习和教学目的，实际应用中可能需要更复杂的错误处理和性能优化。
