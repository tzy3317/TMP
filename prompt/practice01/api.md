# Cue-Pro API 设计文档

> 本文档规划项目中所有模块的方法、变量及伪代码，作为编码实现的直接依据。
> 版本：v1.0.0 | 最后更新：2026-05-06
> 依赖规范：[spec.md](spec.md) | [requirement.md](requirement.md)

---

## 1. 模块总览

```
Cue-Pro/
├── config.py              # 配置管理模块
├── llm_client.py          # LLM 客户端模块
├── validator.py           # 配置校验模块
├── exceptions.py          # 自定义异常
└── main.py                # 应用入口
```

| 模块 | 职责 | 依赖 |
|------|------|------|
| `config.py` | 环境变量加载、配置集中管理、默认值维护 | `python-dotenv`, `os` |
| `validator.py` | 必配项校验、格式校验 | `config.py` |
| `exceptions.py` | 自定义异常类定义 | 无 |
| `llm_client.py` | LLM 调用封装、参数组装 | `openai`, `config.py` |
| `main.py` | 应用入口、启动流程 | 所有模块 |

---

## 2. exceptions.py

### 2.1 ConfigError

| 属性 | 值 |
|------|-----|
| 继承 | `Exception` |
| 用途 | 配置相关错误的基类 |

```python
class ConfigError(Exception):
    """配置错误基类"""
    pass
```

---

### 2.2 MissingConfigError

| 属性 | 值 |
|------|-----|
| 继承 | `ConfigError` |
| 用途 | 必配项缺失时抛出 |

```python
class MissingConfigError(ConfigError):
    """必配环境变量缺失"""
    
    VARIABLE: str
    
    def __init__(self, variable: str) -> None:
        self.VARIABLE = variable
        message = f"配置错误：环境变量 '{variable}' 未设置。\n请检查 .env 文件"
        super().__init__(message)
```

**Pseudocode:**
```
CLASS MissingConfigError EXTENDS ConfigError:
    
    METHOD __init__(variable):
        self.VARIABLE = variable
        template = "配置错误：环境变量 '{var}' 未设置。\n请检查 .env 文件"
        message = FORMAT(template, var=variable)
        CALL Parent.__init__(message)
```

---

### 2.3 InvalidConfigError

| 属性 | 值 |
|------|-----|
| 继承 | `ConfigError` |
| 用途 | 配置值格式非法时抛出 |

```python
class InvalidConfigError(ConfigError):
    """配置值格式错误"""
    
    VARIABLE: str
    VALUE: str
    REASON: str
    
    def __init__(self, variable: str, value: str, reason: str) -> None:
        self.VARIABLE = variable
        self.VALUE = self._mask(value)
        self.REASON = reason
        message = f"配置错误：'{variable}' 的值无效。\n原因：{reason}\n当前值：{self.VALUE}"
        super().__init__(message)
    
    @staticmethod
    def _mask(value: str) -> str:
        return value[:4] + "***" + value[-4:] if len(value) > 8 else "***"
```

**Pseudocode:**
```
CLASS InvalidConfigError EXTENDS ConfigError:
    
    METHOD __init__(variable, value, reason):
        self.VARIABLE = variable
        self.VALUE = CALL _mask(value)
        self.REASON = reason
        template = "配置错误：'{var}' 的值无效。\n原因：{r}\n当前值：{v}"
        message = FORMAT(template, var=variable, r=reason, v=self.VALUE)
        CALL Parent.__init__(message)
    
    STATIC METHOD _mask(value):
        IF LENGTH(value) > 8:
            RETURN SUBSTRING(value, 0, 4) + "***" + SUBSTRING(value, -4)
        ELSE:
            RETURN "***"
```

---

## 3. config.py

### 3.1 模块常量

| 常量名 | 类型 | 值 | 说明 |
|--------|------|-----|------|
| `_REQUIRED_VARS` | `list[str]` | `["LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"]` | 必配项列表 |
| `_DEFAULT_TIMEOUT` | `int` | `60` | 请求超时默认值 |
| `_DEFAULT_MAX_TOKENS` | `int` | `4096` | 最大 Token 默认值 |
| `_DEFAULT_TEMPERATURE` | `float` | `0.7` | Temperature 默认值 |
| `_DEFAULT_TOP_P` | `float` | `1.0` | Top-P 默认值 |

---

### 3.2 LLMConfig 数据类

| 属性 | 值 |
|------|-----|
| 类型 | `dataclass` |
| 用途 | 封装所有 LLM 相关配置 |
| 特性 | `frozen=True` 不可变 |

```python
@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    model: str
    api_key: str
    timeout: int = _DEFAULT_TIMEOUT
    max_tokens: int = _DEFAULT_MAX_TOKENS
    temperature: float = _DEFAULT_TEMPERATURE
    top_p: float = _DEFAULT_TOP_P
```

---

### 3.3 模块级变量

#### `LLM_CONFIG`

| 属性 | 值 |
|------|-----|
| 类型 | `LLMConfig` |
| 作用域 | 模块级单例 |
| 初始化 | 模块导入时自动执行 |

```python
LLM_CONFIG: LLMConfig = _build_config()
```

---

### 3.4 _load_env_file()

| 属性 | 值 |
|------|-----|
| 可见性 | 私有 |
| 参数 | 无 |
| 返回值 | `None` |
| 副作用 | 加载 `.env` 到环境变量 |

```python
def _load_env_file() -> None:
    """加载 .env 文件到环境变量"""
    pass
```

**Pseudocode:**
```
FUNCTION _load_env_file():
    root_dir = GET_DIRECTORY_OF(__file__)
    env_path = JOIN_PATH(root_dir, ".env")
    IF FILE_EXISTS(env_path):
        CALL dotenv.load_dotenv(env_path, override=True)
    ELSE:
        PASS
```

---

### 3.5 _get_env_var(name)

| 属性 | 值 |
|------|-----|
| 可见性 | 私有 |
| 参数 | `name: str` |
| 返回值 | `str | None` |

```python
def _get_env_var(name: str) -> str | None:
    """获取环境变量，空字符串视为 None"""
    pass
```

**Pseudocode:**
```
FUNCTION _get_env_var(name):
    value = os.getenv(name)
    IF value IS None OR STRIP(value) == "":
        RETURN None
    RETURN STRIP(value)
```

---

### 3.6 _validate_required_vars()

| 属性 | 值 |
|------|-----|
| 可见性 | 私有 |
| 参数 | 无 |
| 返回值 | `dict[str, str]` |
| 异常 | `MissingConfigError` |

```python
def _validate_required_vars() -> dict[str, str]:
    """校验必配项，全部存在则返回名值映射"""
    pass
```

**Pseudocode:**
```
FUNCTION _validate_required_vars():
    result = EMPTY_DICTIONARY
    missing = EMPTY_LIST
    FOR var_name IN _REQUIRED_VARS:
        value = CALL _get_env_var(var_name)
        IF value IS None:
            APPEND var_name TO missing
        ELSE:
            result[var_name] = value
    IF LENGTH(missing) > 0:
        RAISE MissingConfigError(missing[0])
    RETURN result
```

---

### 3.7 _validate_url_format(url)

| 属性 | 值 |
|------|-----|
| 可见性 | 私有 |
| 参数 | `url: str` |
| 返回值 | `None` |
| 异常 | `InvalidConfigError` |

```python
def _validate_url_format(url: str) -> None:
    """校验 LLM_BASE_URL 格式"""
    pass
```

**Pseudocode:**
```
FUNCTION _validate_url_format(url):
    IF NOT (STARTS_WITH(url, "http://") OR STARTS_WITH(url, "https://")):
        RAISE InvalidConfigError(
            variable="LLM_BASE_URL",
            value=url,
            reason="必须以 http:// 或 https:// 开头"
        )
    IF NOT ENDS_WITH(url, "/v1"):
        RAISE InvalidConfigError(
            variable="LLM_BASE_URL",
            value=url,
            reason="必须以 /v1 结尾"
        )
    IF ENDS_WITH(url, "/v1/"):
        RAISE InvalidConfigError(
            variable="LLM_BASE_URL",
            value=url,
            reason="末尾有多余斜杠，应为 /v1 而非 /v1/"
        )
```

---

### 3.8 _mask_key(key)

| 属性 | 值 |
|------|-----|
| 可见性 | 私有 |
| 参数 | `key: str` |
| 返回值 | `str` |

```python
def _mask_key(key: str) -> str:
    """API Key 脱敏处理"""
    pass
```

**Pseudocode:**
```
FUNCTION _mask_key(key):
    IF LENGTH(key) <= 8:
        RETURN "***"
    prefix = SUBSTRING(key, 0, 4)
    suffix = SUBSTRING(key, -4)
    RETURN prefix + "***...***" + suffix
```

---

### 3.9 _build_config()

| 属性 | 值 |
|------|-----|
| 可见性 | 私有 |
| 参数 | 无 |
| 返回值 | `LLMConfig` |
| 异常 | `MissingConfigError`, `InvalidConfigError` |

```python
def _build_config() -> LLMConfig:
    """构建 LLMConfig 实例"""
    pass
```

**Pseudocode:**
```
FUNCTION _build_config():
    CALL _load_env_file()
    required = CALL _validate_required_vars()
    CALL _validate_url_format(required["LLM_BASE_URL"])
    config = NEW LLMConfig(
        base_url=required["LLM_BASE_URL"],
        model=required["LLM_MODEL"],
        api_key=required["LLM_API_KEY"]
    )
    RETURN config
```

---

## 4. validator.py

### 4.1 check_config()

| 属性 | 值 |
|------|-----|
| 可见性 | 公共 |
| 参数 | 无 |
| 返回值 | `dict` |

```python
def check_config() -> dict:
    """检查配置状态，返回详细报告"""
    pass
```

**Pseudocode:**
```
FUNCTION check_config():
    report = {
        "status": "unknown",
        "items": EMPTY_LIST,
        "errors": EMPTY_LIST
    }
    FOR var_name IN _REQUIRED_VARS:
        value = CALL _get_env_var(var_name)
        IF value IS None:
            APPEND {
                "name": var_name,
                "status": "missing",
                "value": None
            } TO report.items
            APPEND f"{var_name}: 未设置" TO report.errors
        ELSE:
            display_value = value
            IF "KEY" IN var_name:
                display_value = CALL _mask_key(value)
            APPEND {
                "name": var_name,
                "status": "ok",
                "value": display_value
            } TO report.items
    url = CALL _get_env_var("LLM_BASE_URL")
    IF url IS NOT None:
        TRY:
            CALL _validate_url_format(url)
            APPEND "LLM_BASE_URL: 格式正确" TO report.items
        EXCEPT InvalidConfigError AS e:
            APPEND e.REASON TO report.errors
    IF LENGTH(report.errors) == 0:
        report.status = "ok"
    ELSE:
        report.status = "error"
    RETURN report
```

---

### 4.2 print_config_report(report)

| 属性 | 值 |
|------|-----|
| 可见性 | 公共 |
| 参数 | `report: dict` |
| 返回值 | `None` |

```python
def print_config_report(report: dict) -> None:
    """打印配置检查报告"""
    pass
```

**Pseudocode:**
```
FUNCTION print_config_report(report):
    PRINT "=== Cue-Pro 配置检查报告 ==="
    PRINT ""
    FOR item IN report.items:
        IF item.status == "ok":
            PRINT f"OK {item.name}: {item.value}"
        ELSE:
            PRINT f"FAIL {item.name}: {item.status}"
    IF report.status == "ok":
        PRINT ""
        PRINT "OK 所有配置项已正确设置"
    ELSE:
        PRINT ""
        PRINT f"FAIL 发现 {LENGTH(report.errors)} 个错误："
        FOR error IN report.errors:
            PRINT f"  - {error}"
```

---

## 5. llm_client.py

### 5.1 模块常量

| 常量名 | 类型 | 值 | 说明 |
|--------|------|-----|------|
| `_SYSTEM_PROMPT` | `str` | `"You are a helpful assistant."` | 默认系统提示词 |

---

### 5.2 LLMClient 类

```python
class LLMClient:
    """LLM 客户端封装类"""
    
    _config: LLMConfig
    _client: OpenAI
    
    def __init__(self, config: LLMConfig | None = None) -> None:
        pass
    
    def chat(self, message: str, system_prompt: str | None = None) -> str:
        pass
    
    def chat_stream(self, message: str, system_prompt: str | None = None):
        pass
```

---

### 5.3 __init__(config)

| 属性 | 值 |
|------|-----|
| 参数 | `config: LLMConfig | None` |
| 返回值 | `None` |

```python
def __init__(self, config: LLMConfig | None = None) -> None:
    """初始化 LLM 客户端"""
    pass
```

**Pseudocode:**
```
METHOD __init__(config=None):
    IF config IS None:
        self._config = IMPORT LLM_CONFIG FROM config
    ELSE:
        self._config = config
    self._client = NEW OpenAI(
        base_url=self._config.base_url,
        api_key=self._config.api_key,
        timeout=self._config.timeout
    )
```

---

### 5.4 chat(message, system_prompt)

| 属性 | 值 |
|------|-----|
| 参数 | `message: str`, `system_prompt: str | None` |
| 返回值 | `str` |

```python
def chat(self, message: str, system_prompt: str | None = None) -> str:
    """发送单轮对话请求，返回完整回复"""
    pass
```

**Pseudocode:**
```
METHOD chat(message, system_prompt=None):
    IF system_prompt IS None:
        system_prompt = _SYSTEM_PROMPT
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    response = CALL self._client.chat.completions.create(
        model=self._config.model,
        messages=messages,
        max_tokens=self._config.max_tokens,
        temperature=self._config.temperature,
        top_p=self._config.top_p
    )
    RETURN response.choices[0].message.content
```

---

### 5.5 chat_stream(message, system_prompt)

| 属性 | 值 |
|------|-----|
| 参数 | `message: str`, `system_prompt: str | None` |
| 返回值 | `Generator[str, None, None]` |

```python
def chat_stream(self, message: str, system_prompt: str | None = None):
    """发送流式对话请求，返回生成器"""
    pass
```

**Pseudocode:**
```
METHOD chat_stream(message, system_prompt=None):
    IF system_prompt IS None:
        system_prompt = _SYSTEM_PROMPT
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    stream = CALL self._client.chat.completions.create(
        model=self._config.model,
        messages=messages,
        max_tokens=self._config.max_tokens,
        temperature=self._config.temperature,
        top_p=self._config.top_p,
        stream=True
    )
    FOR chunk IN stream:
        delta = chunk.choices[0].delta.content
        IF delta IS NOT None AND delta != "":
            YIELD delta
```

---

## 6. main.py

### 6.1 main()

| 属性 | 值 |
|------|-----|
| 参数 | 无 |
| 返回值 | `None` |

```python
def main() -> None:
    """应用主入口"""
    pass
```

**Pseudocode:**
```
FUNCTION main():
    PRINT "=== Cue-Pro 启动 ==="
    PRINT ""
    FROM config IMPORT LLM_CONFIG
    FROM llm_client IMPORT LLMClient
    PRINT "OK 配置加载成功"
    PRINT f"  服务商: {LLM_CONFIG.base_url}"
    PRINT f"  模型: {LLM_CONFIG.model}"
    PRINT ""
    client = NEW LLMClient()
    PRINT ">>> 发送测试消息..."
    response = CALL client.chat("你好，请简单介绍一下自己。")
    PRINT f"<<< {response}"
```

---

### 6.2 if __name__ == "__main__"

**Pseudocode:**
```
IF __name__ == "__main__":
    TRY:
        CALL main()
    EXCEPT KeyboardInterrupt:
        PRINT "程序被用户中断"
    EXCEPT Exception AS e:
        PRINT f"程序异常: {e}"
        EXIT(1)
```

---

## 7. 调用关系图

```
main.py
    |
    ├── IMPORT config.py ---→ 触发模块初始化
    |       |
    |       ├── _load_env_file()          # 加载 .env
    |       ├── _validate_required_vars() # 校验必配项
    |       ├── _validate_url_format()    # 校验 URL
    |       └── LLM_CONFIG = _build_config() # 构建单例
    |
    ├── IMPORT llm_client.py
    |       |
    |       └── LLMClient
    |               |
    |               ├── __init__(config)  # 引用 LLM_CONFIG
    |               ├── chat()            # 同步调用
    |               └── chat_stream()     # 流式调用
    |
    └── IMPORT validator.py
            |
            ├── check_config()            # 显式校验
            └── print_config_report()     # 打印报告
```

---

## 8. 变量汇总表

### 8.1 全局变量

| 变量名 | 模块 | 类型 | 作用域 | 说明 |
|--------|------|------|--------|------|
| `LLM_CONFIG` | `config.py` | `LLMConfig` | 模块级单例 | 全局配置实例 |
| `_REQUIRED_VARS` | `config.py` | `list[str]` | 模块私有 | 必配项列表 |
| `_DEFAULT_*` | `config.py` | 多种 | 模块私有 | 各参数默认值 |
| `_SYSTEM_PROMPT` | `llm_client.py` | `str` | 模块私有 | 默认系统提示词 |

### 8.2 类实例变量

| 变量名 | 所属类 | 类型 | 说明 |
|--------|--------|------|------|
| `base_url` | `LLMConfig` | `str` | API 基础地址 |
| `model` | `LLMConfig` | `str` | 模型名称 |
| `api_key` | `LLMConfig` | `str` | API 密钥 |
| `timeout` | `LLMConfig` | `int` | 超时时间 |
| `max_tokens` | `LLMConfig` | `int` | 最大 Token 数 |
| `temperature` | `LLMConfig` | `float` | 随机性控制 |
| `top_p` | `LLMConfig` | `float` | 核采样阈值 |
| `_config` | `LLMClient` | `LLMConfig` | 配置引用 |
| `_client` | `LLMClient` | `OpenAI` | 底层客户端 |

---

## 9. 异常处理矩阵

| 方法 | 可能异常 | 处理方式 |
|------|---------|---------|
| `_build_config()` | `MissingConfigError` | 向上抛出，模块初始化时捕获并退出 |
| `_build_config()` | `InvalidConfigError` | 向上抛出，模块初始化时捕获并退出 |
| `chat()` | API 网络异常 | 向上抛出，由调用方处理 |
| `chat()` | API 认证失败 | 向上抛出，由调用方处理 |
| `chat_stream()` | API 网络异常 | 生成器内部抛出，由消费方处理 |
| `check_config()` | 无 | 不抛出异常，返回报告字典 |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-05-06 | 初始版本，定义 5 个模块的完整 API |

---

## 11. 相关文档

| 文档 | 说明 |
|------|------|
| [spec.md](spec.md) | 项目技术规范 |
| [requirement.md](requirement.md) | 功能与非功能需求 |

---

*本文档由 Cue-Pro 项目维护，API 变更需同步更新本文档。*