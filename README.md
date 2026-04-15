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
- 支持 Ctrl+C 退出

**教学目标**：
- 学习如何实现流式 API 调用
- 了解如何处理 SSE（Server-Sent Events）格式的响应
- 掌握聊天历史管理和上下文维护
- 学习终端交互和异常处理

**核心功能**：
- `load_dotenv()`: 从项目根目录加载 .env 文件
- `call_llm_stream()`: 流式调用 LLM API
- `main()`: 主函数，处理用户输入和聊天循环

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

**功能**：启动交互式聊天客户端，支持流式输出和历史记录。

**使用方法**：
1. 输入你的问题或消息
2. 等待助手的响应（流式输出）
3. 继续输入新的问题
4. 按 Ctrl+C 退出聊天

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
