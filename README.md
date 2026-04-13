# AI 智能体开发学习项目

## 项目简介

本项目是一个基于 Python 的 AI 智能体开发学习框架，旨在帮助开发者理解如何使用标准库与 LLM（大语言模型）进行交互。项目包含了基本的环境配置、API 调用和统计功能，为学习 AI 智能体开发提供了基础示例。

## 项目结构

```
├── .env               # 环境配置文件（用户创建）
├── .env.example       # 环境配置模板
├── practice01/        # 练习目录
│   ├── call_llm.py    # LLM API 调用脚本
│   └── llm_client.py  # LLM 客户端（模拟实现）
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
