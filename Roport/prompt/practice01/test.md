# Cue-Pro 测试文档

> 本文档定义项目的测试策略、测试用例及测试代码规范。
> 版本：v1.0.0 | 最后更新：2026-05-06
> 依赖规范：[spec.md](spec.md) | [requirement.md](requirement.md) | [api.md](api.md)

---

## 1. 测试策略

### 1.1 测试层级

| 层级 | 范围 | 工具 | 目标 |
|------|------|------|------|
| 单元测试 | 单个函数/方法 | `pytest` | 验证逻辑正确性 |
| 集成测试 | 模块间协作 | `pytest` | 验证模块集成 |
| 端到端测试 | 完整启动流程 | `pytest` + 子进程 | 验证应用可运行 |

### 1.2 测试目录结构

```
tests/
├── __init__.py
├── conftest.py          # pytest 共享 fixture
├── test_exceptions.py    # 异常类测试
├── test_config.py       # 配置模块测试
├── test_validator.py    # 校验模块测试
├── test_llm_client.py   # LLM 客户端测试（mock）
└── test_e2e.py          # 端到端测试
```

### 1.3 测试原则

1. **每个 public function 至少一个测试用例**
2. **边界条件必须覆盖**：空值、非法格式、极值
3. **敏感信息绝不使用真实值**：测试中使用假密钥
4. **外部 API 必须 Mock**：LLM 调用使用 mock 对象
5. **环境隔离**：每个测试独立设置/清理环境变量

---

## 2. 测试环境配置

### 2.1 conftest.py — 共享 Fixture

```python
import pytest
import os
from unittest.mock import patch, MagicMock

# 测试用合法配置
VALID_CONFIG = {
    "LLM_BASE_URL": "https://api.openai.com/v1",
    "LLM_MODEL": "gpt-4o",
    "LLM_API_KEY": "sk-test1234567890abcdef",
}

# 测试用非法配置
INVALID_URL_CONFIG = {
    "LLM_BASE_URL": "invalid-url",
    "LLM_MODEL": "gpt-4o",
    "LLM_API_KEY": "sk-test1234567890abcdef",
}

@pytest.fixture
def clean_env():
    """清理环境变量的 fixture"""
    # 保存原始环境
    original = {}
    for key in VALID_CONFIG.keys():
        original[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]
    yield
    # 恢复原始环境
    for key, value in original.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

@pytest.fixture
def valid_env(clean_env):
    """设置合法环境变量的 fixture"""
    for key, value in VALID_CONFIG.items():
        os.environ[key] = value
    yield

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI 客户端"""
    with patch('llm_client.OpenAI') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client
```

**Pseudocode:**
```
FIXTURE clean_env:
    # 保存原始环境变量状态
    backup = COPY_OF(os.environ)
    # 删除所有测试相关的环境变量
    FOR key IN [LLM_BASE_URL, LLM_MODEL, LLM_API_KEY]:
        IF key IN os.environ:
            DELETE os.environ[key]
    YIELD
    # 测试结束后恢复原始状态
    os.environ = backup

FIXTURE valid_env DEPENDS_ON clean_env:
    # 设置测试用的合法环境变量
    os.environ[LLM_BASE_URL] = "https://api.openai.com/v1"
    os.environ[LLM_MODEL] = "gpt-4o"
    os.environ[LLM_API_KEY] = "sk-test1234567890abcdef"
    YIELD

FIXTURE mock_openai_client:
    # 使用 unittest.mock.patch 替换 OpenAI 类
    WITH PATCH('llm_client.OpenAI') AS mock_class:
        mock_instance = CREATE_MOCK()
        mock_class.return_value = mock_instance
        YIELD mock_instance
```

---

## 3. 单元测试

### 3.1 test_exceptions.py

#### test_missing_config_error_message

| 属性 | 值 |
|------|-----|
| 目标 | `MissingConfigError` |
| 场景 | 构造异常并验证消息内容 |
| 断言 | 消息包含变量名和提示 |

```python
def test_missing_config_error_message():
    """测试 MissingConfigError 消息格式"""
    from exceptions import MissingConfigError
    
    err = MissingConfigError("LLM_API_KEY")
    assert "LLM_API_KEY" in str(err)
    assert ".env" in str(err)
    assert err.VARIABLE == "LLM_API_KEY"
```

**Pseudocode:**
```
TEST test_missing_config_error_message:
    CREATE err = MissingConfigError("LLM_API_KEY")
    ASSERT "LLM_API_KEY" IS_IN STRING(err)
    ASSERT ".env" IS_IN STRING(err)
    ASSERT err.VARIABLE EQUALS "LLM_API_KEY"
```

---

#### test_invalid_config_error_masking

| 属性 | 值 |
|------|-----|
| 目标 | `InvalidConfigError` |
| 场景 | 验证敏感信息脱敏 |
| 断言 | 消息中的密钥已被脱敏 |

```python
def test_invalid_config_error_masking():
    """测试 InvalidConfigError 脱敏处理"""
    from exceptions import InvalidConfigError
    
    err = InvalidConfigError("LLM_API_KEY", "sk-1234567890abcdef", "格式错误")
    assert "sk-***" in str(err)
    assert "1234567890abcdef" not in str(err)
    assert err.REASON == "格式错误"
```

**Pseudocode:**
```
TEST test_invalid_config_error_masking:
    CREATE err = InvalidConfigError("LLM_API_KEY", "sk-1234567890abcdef", "格式错误")
    ASSERT "sk-***" IS_IN STRING(err)
    ASSERT "1234567890abcdef" NOT_IN STRING(err)
    ASSERT err.REASON EQUALS "格式错误"
```

---

### 3.2 test_config.py

#### test_load_env_file_exists

| 属性 | 值 |
|------|-----|
| 目标 | `_load_env_file()` |
| 场景 | `.env` 文件存在时正确加载 |
| 断言 | 环境变量被正确设置 |

```python
def test_load_env_file_exists(tmp_path, clean_env):
    """测试 .env 文件存在时的加载"""
    from config import _load_env_file
    import dotenv
    
    # 创建临时 .env 文件
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_MODEL=test-model\n")
    
    # 临时修改项目根目录
    with patch('config.__file__', str(tmp_path / 'config.py')):
        _load_env_file()
        assert os.environ.get("LLM_MODEL") == "test-model"
```

**Pseudocode:**
```
TEST test_load_env_file_exists:
    # 创建临时目录和 .env 文件
    temp_dir = CREATE_TEMP_DIRECTORY()
    env_file = CREATE_FILE(temp_dir / ".env")
    WRITE_TO_FILE(env_file, "LLM_MODEL=test-model\n")
    
    # Mock __file__ 路径使模块认为根目录是 temp_dir
    WITH PATCH config.__file__ TO temp_dir/config.py:
        CALL _load_env_file()
        ASSERT os.environ[LLM_MODEL] EQUALS "test-model"
```

---

#### test_load_env_file_not_exists

| 属性 | 值 |
|------|-----|
| 目标 | `_load_env_file()` |
| 场景 | `.env` 文件不存在时静默跳过 |
| 断言 | 不抛出异常 |

```python
def test_load_env_file_not_exists(tmp_path, clean_env):
    """测试 .env 文件不存在时静默跳过"""
    from config import _load_env_file
    
    # 使用空目录（无 .env 文件）
    with patch('config.__file__', str(tmp_path / 'config.py')):
        _load_env_file()  # 不应抛出异常
        assert "LLM_MODEL" not in os.environ
```

**Pseudocode:**
```
TEST test_load_env_file_not_exists:
    temp_dir = CREATE_TEMP_DIRECTORY()  # 空目录，无 .env
    WITH PATCH config.__file__ TO temp_dir/config.py:
        CALL _load_env_file()  # 应正常执行不报错
        ASSERT LLM_MODEL NOT_IN os.environ
```

---

#### test_get_env_var_empty_string

| 属性 | 值 |
|------|-----|
| 目标 | `_get_env_var()` |
| 场景 | 环境变量值为空字符串 |
| 断言 | 返回 `None` |

```python
def test_get_env_var_empty_string(clean_env):
    """测试空字符串被视为 None"""
    from config import _get_env_var
    
    os.environ["TEST_VAR"] = ""
    assert _get_env_var("TEST_VAR") is None
    
    os.environ["TEST_VAR"] = "   "
    assert _get_env_var("TEST_VAR") is None
```

**Pseudocode:**
```
TEST test_get_env_var_empty_string:
    os.environ[TEST_VAR] = ""
    ASSERT CALL _get_env_var(TEST_VAR) IS None
    os.environ[TEST_VAR] = "   "
    ASSERT CALL _get_env_var(TEST_VAR) IS None
```

---

#### test_validate_required_vars_all_present

| 属性 | 值 |
|------|-----|
| 目标 | `_validate_required_vars()` |
| 场景 | 所有必配项都存在 |
| 断言 | 返回包含所有键的字典 |

```python
def test_validate_required_vars_all_present(valid_env):
    """测试所有必配项存在时通过校验"""
    from config import _validate_required_vars
    
    result = _validate_required_vars()
    assert "LLM_BASE_URL" in result
    assert "LLM_MODEL" in result
    assert "LLM_API_KEY" in result
    assert result["LLM_BASE_URL"] == "https://api.openai.com/v1"
```

**Pseudocode:**
```
TEST test_validate_required_vars_all_present:
    # 使用 valid_env fixture 设置环境
    result = CALL _validate_required_vars()
    ASSERT "LLM_BASE_URL" IS_IN result
    ASSERT "LLM_MODEL" IS_IN result
    ASSERT "LLM_API_KEY" IS_IN result
    ASSERT result[LLM_BASE_URL] EQUALS "https://api.openai.com/v1"
```

---

#### test_validate_required_vars_missing

| 属性 | 值 |
|------|-----|
| 目标 | `_validate_required_vars()` |
| 场景 | 缺少必配项 |
| 断言 | 抛出 `MissingConfigError` |

```python
def test_validate_required_vars_missing(clean_env):
    """测试缺少必配项时抛出异常"""
    from config import _validate_required_vars
    from exceptions import MissingConfigError
    
    with pytest.raises(MissingConfigError) as exc_info:
        _validate_required_vars()
    assert "LLM_BASE_URL" in str(exc_info.value)
```

**Pseudocode:**
```
TEST test_validate_required_vars_missing:
    # clean_env 确保无环境变量
    ASSERT RAISES MissingConfigError:
        CALL _validate_required_vars()
    ASSERT "LLM_BASE_URL" IS_IN error_message
```

---

#### test_validate_url_format_valid

| 属性 | 值 |
|------|-----|
| 目标 | `_validate_url_format()` |
| 场景 | 合法 URL 格式 |
| 断言 | 不抛出异常 |

```python
def test_validate_url_format_valid():
    """测试合法 URL 通过校验"""
    from config import _validate_url_format
    
    # 以下不应抛出异常
    _validate_url_format("https://api.openai.com/v1")
    _validate_url_format("http://localhost:11434/v1")
    _validate_url_format("https://api.moonshot.cn/v1")
```

**Pseudocode:**
```
TEST test_validate_url_format_valid:
    CALL _validate_url_format("https://api.openai.com/v1")  # 应通过
    CALL _validate_url_format("http://localhost:11434/v1")  # 应通过
    CALL _validate_url_format("https://api.moonshot.cn/v1")  # 应通过
    # 无异常即通过
```

---

#### test_validate_url_format_invalid

| 属性 | 值 |
|------|-----|
| 目标 | `_validate_url_format()` |
| 场景 | 非法 URL 格式 |
| 断言 | 抛出 `InvalidConfigError` |

```python
def test_validate_url_format_invalid():
    """测试非法 URL 抛出异常"""
    from config import _validate_url_format
    from exceptions import InvalidConfigError
    
    invalid_urls = [
        "api.openai.com/v1",           # 缺少协议头
        "https://api.openai.com",      # 缺少 /v1
        "https://api.openai.com/v1/",  # 多余斜杠
        "ftp://api.openai.com/v1",     # 错误协议
    ]
    
    for url in invalid_urls:
        with pytest.raises(InvalidConfigError):
            _validate_url_format(url)
```

**Pseudocode:**
```
TEST test_validate_url_format_invalid:
    invalid_urls = [
        "api.openai.com/v1",
        "https://api.openai.com",
        "https://api.openai.com/v1/",
        "ftp://api.openai.com/v1"
    ]
    FOR url IN invalid_urls:
        ASSERT RAISES InvalidConfigError:
            CALL _validate_url_format(url)
```

---

#### test_mask_key_long

| 属性 | 值 |
|------|-----|
| 目标 | `_mask_key()` |
| 场景 | 长密钥脱敏 |
| 断言 | 中间部分被替换 |

```python
def test_mask_key_long():
    """测试长密钥脱敏"""
    from config import _mask_key
    
    key = "sk-1234567890abcdef"
    masked = _mask_key(key)
    assert masked == "sk-1***...***cdef"
    assert "1234567890ab" not in masked
```

**Pseudocode:**
```
TEST test_mask_key_long:
    key = "sk-1234567890abcdef"
    result = CALL _mask_key(key)
    ASSERT result EQUALS "sk-1***...***cdef"
    ASSERT "1234567890ab" NOT_IN result
```

---

#### test_mask_key_short

| 属性 | 值 |
|------|-----|
| 目标 | `_mask_key()` |
| 场景 | 短密钥脱敏 |
| 断言 | 全部替换为 *** |

```python
def test_mask_key_short():
    """测试短密钥脱敏"""
    from config import _mask_key
    
    assert _mask_key("short") == "***"
    assert _mask_key("12345678") == "***"
```

**Pseudocode:**
```
TEST test_mask_key_short:
    ASSERT CALL _mask_key("short") EQUALS "***"
    ASSERT CALL _mask_key("12345678") EQUALS "***"
```

---

#### test_build_config_success

| 属性 | 值 |
|------|-----|
| 目标 | `_build_config()` |
| 场景 | 合法配置构建成功 |
| 断言 | 返回 `LLMConfig` 实例且字段正确 |

```python
def test_build_config_success(valid_env):
    """测试合法配置构建成功"""
    from config import _build_config, LLMConfig
    
    config = _build_config()
    assert isinstance(config, LLMConfig)
    assert config.base_url == "https://api.openai.com/v1"
    assert config.model == "gpt-4o"
    assert config.api_key == "sk-test1234567890abcdef"
    assert config.timeout == 60  # 默认值
    assert config.max_tokens == 4096  # 默认值
    assert config.temperature == 0.7  # 默认值
```

**Pseudocode:**
```
TEST test_build_config_success:
    config = CALL _build_config()
    ASSERT config IS_INSTANCE_OF LLMConfig
    ASSERT config.base_url EQUALS "https://api.openai.com/v1"
    ASSERT config.model EQUALS "gpt-4o"
    ASSERT config.api_key EQUALS "sk-test1234567890abcdef"
    ASSERT config.timeout EQUALS 60
    ASSERT config.max_tokens EQUALS 4096
    ASSERT config.temperature EQUALS 0.7
```

---

#### test_build_config_missing_raises

| 属性 | 值 |
|------|-----|
| 目标 | `_build_config()` |
| 场景 | 缺少配置时构建失败 |
| 断言 | 抛出 `MissingConfigError` |

```python
def test_build_config_missing_raises(clean_env):
    """测试缺少配置时抛出异常"""
    from config import _build_config
    from exceptions import MissingConfigError
    
    with pytest.raises(MissingConfigError):
        _build_config()
```

**Pseudocode:**
```
TEST test_build_config_missing_raises:
    ASSERT RAISES MissingConfigError:
        CALL _build_config()
```

---

### 3.3 test_validator.py

#### test_check_config_all_ok

| 属性 | 值 |
|------|-----|
| 目标 | `check_config()` |
| 场景 | 所有配置正确 |
| 断言 | 返回 status=ok，无 errors |

```python
def test_check_config_all_ok(valid_env):
    """测试配置完整时返回 ok"""
    from validator import check_config
    
    report = check_config()
    assert report["status"] == "ok"
    assert len(report["errors"]) == 0
    assert len(report["items"]) >= 3
    
    # 验证 API Key 已脱敏
    key_item = [i for i in report["items"] if i["name"] == "LLM_API_KEY"][0]
    assert "***" in key_item["value"]
    assert "sk-test1234567890abcdef" not in key_item["value"]
```

**Pseudocode:**
```
TEST test_check_config_all_ok:
    report = CALL check_config()
    ASSERT report.status EQUALS "ok"
    ASSERT LENGTH(report.errors) EQUALS 0
    # 检查 API Key 脱敏
    key_item = FIND report.items WHERE name == LLM_API_KEY
    ASSERT "***" IS_IN key_item.value
    ASSERT "sk-test1234567890abcdef" NOT_IN key_item.value
```

---

#### test_check_config_missing

| 属性 | 值 |
|------|-----|
| 目标 | `check_config()` |
| 场景 | 缺少配置项 |
| 断言 | 返回 status=error，包含缺失项 |

```python
def test_check_config_missing(clean_env):
    """测试缺少配置时返回 error"""
    from validator import check_config
    
    report = check_config()
    assert report["status"] == "error"
    assert len(report["errors"]) > 0
    assert any("LLM_BASE_URL" in e for e in report["errors"])
```

**Pseudocode:**
```
TEST test_check_config_missing:
    report = CALL check_config()
    ASSERT report.status EQUALS "error"
    ASSERT LENGTH(report.errors) > 0
    ASSERT ANY error WHERE "LLM_BASE_URL" IS_IN error
```

---

#### test_print_config_report

| 属性 | 值 |
|------|-----|
| 目标 | `print_config_report()` |
| 场景 | 打印配置报告 |
| 断言 | 输出包含预期内容 |

```python
def test_print_config_report(capsys):
    """测试打印报告输出格式"""
    from validator import print_config_report
    
    report = {
        "status": "ok",
        "items": [
            {"name": "LLM_MODEL", "status": "ok", "value": "gpt-4o"},
        ],
        "errors": []
    }
    
    print_config_report(report)
    captured = capsys.readouterr()
    assert "Cue-Pro 配置检查报告" in captured.out
    assert "OK" in captured.out
    assert "gpt-4o" in captured.out
```

**Pseudocode:**
```
TEST test_print_config_report:
    report = CREATE_TEST_REPORT(status="ok", items=[{name: LLM_MODEL, status: ok, value: gpt-4o}])
    CALL print_config_report(report)
    output = CAPTURE_STDOUT()
    ASSERT "Cue-Pro 配置检查报告" IS_IN output
    ASSERT "OK" IS_IN output
    ASSERT "gpt-4o" IS_IN output
```

---

### 3.4 test_llm_client.py

#### test_llm_client_init_with_config

| 属性 | 值 |
|------|-----|
| 目标 | `LLMClient.__init__()` |
| 场景 | 传入自定义配置初始化 |
| 断言 | 内部配置和客户端正确设置 |

```python
def test_llm_client_init_with_config(mock_openai_client):
    """测试传入配置初始化客户端"""
    from llm_client import LLMClient
    from config import LLMConfig
    
    config = LLMConfig(
        base_url="https://test.com/v1",
        model="test-model",
        api_key="sk-test",
    )
    
    client = LLMClient(config)
    assert client._config == config
    assert client._client is mock_openai_client
```

**Pseudocode:**
```
TEST test_llm_client_init_with_config:
    config = NEW LLMConfig(base_url="https://test.com/v1", model="test-model", api_key="sk-test")
    client = NEW LLMClient(config)
    ASSERT client._config EQUALS config
    ASSERT client._client IS mock_openai_client
```

---

#### test_llm_client_init_default_config

| 属性 | 值 |
|------|-----|
| 目标 | `LLMClient.__init__()` |
| 场景 | 使用默认全局配置初始化 |
| 断言 | 引用全局 `LLM_CONFIG` |

```python
def test_llm_client_init_default_config(valid_env, mock_openai_client):
    """测试使用默认配置初始化"""
    from llm_client import LLMClient
    from config import LLM_CONFIG
    
    client = LLMClient()
    assert client._config is LLM_CONFIG
```

**Pseudocode:**
```
TEST test_llm_client_init_default_config:
    client = NEW LLMClient()  # 不传 config
    ASSERT client._config IS LLM_CONFIG
```

---

#### test_chat_success

| 属性 | 值 |
|------|-----|
| 目标 | `LLMClient.chat()` |
| 场景 | 正常对话返回结果 |
| 断言 | 返回模型生成的文本 |

```python
def test_chat_success(mock_openai_client):
    """测试正常对话"""
    from llm_client import LLMClient
    from config import LLMConfig
    
    # 设置 mock 返回值
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello, I am an AI."
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    config = LLMConfig(
        base_url="https://test.com/v1",
        model="test-model",
        api_key="sk-test",
    )
    client = LLMClient(config)
    
    result = client.chat("Hi")
    assert result == "Hello, I am an AI."
    
    # 验证调用参数
    call_args = mock_openai_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "test-model"
    assert "messages" in call_args[1]
```

**Pseudocode:**
```
TEST test_chat_success:
    # 准备 mock 响应
    mock_response = CREATE_MOCK()
    mock_response.choices[0].message.content = "Hello, I am an AI."
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    config = NEW LLMConfig(...)
    client = NEW LLMClient(config)
    result = CALL client.chat("Hi")
    ASSERT result EQUALS "Hello, I am an AI."
    
    # 验证 API 调用参数
    args = GET_CALL_ARGUMENTS(mock_openai_client.chat.completions.create)
    ASSERT args.model EQUALS "test-model"
    ASSERT args.messages EXISTS
```

---

#### test_chat_with_custom_system_prompt

| 属性 | 值 |
|------|-----|
| 目标 | `LLMClient.chat()` |
| 场景 | 使用自定义系统提示词 |
| 断言 | 消息列表包含自定义 system prompt |

```python
def test_chat_with_custom_system_prompt(mock_openai_client):
    """测试自定义系统提示词"""
    from llm_client import LLMClient
    from config import LLMConfig
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "OK"
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    config = LLMConfig(
        base_url="https://test.com/v1",
        model="test-model",
        api_key="sk-test",
    )
    client = LLMClient(config)
    
    client.chat("Hello", system_prompt="You are a coder.")
    
    call_args = mock_openai_client.chat.completions.create.call_args[1]
    assert call_args["messages"][0]["role"] == "system"
    assert call_args["messages"][0]["content"] == "You are a coder."
    assert call_args["messages"][1]["role"] == "user"
```

**Pseudocode:**
```
TEST test_chat_with_custom_system_prompt:
    SETUP mock_response
    client = NEW LLMClient(config)
    CALL client.chat("Hello", system_prompt="You are a coder.")
    args = GET_CALL_ARGUMENTS(mock_openai_client.chat.completions.create)
    ASSERT args.messages[0].role EQUALS "system"
    ASSERT args.messages[0].content EQUALS "You are a coder."
    ASSERT args.messages[1].role EQUALS "user"
```

---

#### test_chat_stream

| 属性 | 值 |
|------|-----|
| 目标 | `LLMClient.chat_stream()` |
| 场景 | 流式输出 |
| 断言 | 返回生成器，逐块 yield 内容 |

```python
def test_chat_stream(mock_openai_client):
    """测试流式对话"""
    from llm_client import LLMClient
    from config import LLMConfig
    
    # 设置 mock 流式响应
    def mock_stream():
        chunks = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=""))]),  # 空内容
        ]
        for chunk in chunks:
            yield chunk
    
    mock_openai_client.chat.completions.create.return_value = mock_stream()
    
    config = LLMConfig(
        base_url="https://test.com/v1",
        model="test-model",
        api_key="sk-test",
    )
    client = LLMClient(config)
    
    result = list(client.chat_stream("Hi"))
    assert result == ["Hello", " world"]
    
    # 验证 stream=True 被传递
    call_args = mock_openai_client.chat.completions.create.call_args[1]
    assert call_args["stream"] is True
```

**Pseudocode:**
```
TEST test_chat_stream:
    # 创建 mock 流数据
    chunks = [
        {content: "Hello"},
        {content: " world"},
        {content: ""}
    ]
    mock_openai_client.chat.completions.create.return_value = chunks
    
    client = NEW LLMClient(config)
    result = CONVERT_TO_LIST(CALL client.chat_stream("Hi"))
    ASSERT result EQUALS ["Hello", " world"]
    
    args = GET_CALL_ARGUMENTS(mock_openai_client.chat.completions.create)
    ASSERT args.stream IS True
```

---

## 4. 集成测试

### 4.1 test_integration_config_to_client

| 属性 | 值 |
|------|-----|
| 目标 | 配置模块 -> 客户端模块 |
| 场景 | 完整链路：环境变量 -> 配置加载 -> 客户端初始化 |
| 断言 | 客户端使用配置模块的单例 |

```python
def test_integration_config_to_client(valid_env, mock_openai_client):
    """测试配置到客户端的集成"""
    from config import LLM_CONFIG
    from llm_client import LLMClient
    
    # 配置模块已在导入时自动加载
    assert LLM_CONFIG.base_url == "https://api.openai.com/v1"
    
    # 客户端使用全局配置
    client = LLMClient()
    assert client._config is LLM_CONFIG
    
    # 验证 OpenAI 客户端被正确初始化
    mock_openai_client.assert_called_once()
    call_kwargs = mock_openai_client.call_args[1]
    assert call_kwargs["base_url"] == "https://api.openai.com/v1"
    assert call_kwargs["api_key"] == "sk-test1234567890abcdef"
    assert call_kwargs["timeout"] == 60
```

**Pseudocode:**
```
TEST test_integration_config_to_client:
    # 导入触发配置加载
    FROM config IMPORT LLM_CONFIG
    FROM llm_client IMPORT LLMClient
    
    ASSERT LLM_CONFIG.base_url EQUALS "https://api.openai.com/v1"
    
    client = NEW LLMClient()
    ASSERT client._config IS LLM_CONFIG
    
    # 验证 OpenAI 类初始化参数
    ASSERT mock_openai_client.CALLED_ONCE
    ASSERT call_kwargs.base_url EQUALS "https://api.openai.com/v1"
    ASSERT call_kwargs.api_key EQUALS "sk-test1234567890abcdef"
    ASSERT call_kwargs.timeout EQUALS 60
```

---

## 5. 端到端测试

### 5.1 test_e2e_missing_env_exit

| 属性 | 值 |
|------|-----|
| 目标 | 应用启动流程 |
| 场景 | 缺少环境变量时程序退出 |
| 断言 | 退出码非零 |

```python
def test_e2e_missing_env_exit(clean_env):
    """测试缺少环境变量时应用退出"""
    import subprocess
    import sys
    
    result = subprocess.run(
        [sys.executable, "-c", "import config"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "LLM_BASE_URL" in result.stderr or "配置错误" in result.stderr
```

**Pseudocode:**
```
TEST test_e2e_missing_env_exit:
    # 在子进程中导入 config 模块（会触发配置加载）
    result = RUN_SUBPROCESS([python, "-c", "import config"])
    ASSERT result.returncode NOT_EQUALS 0
    ASSERT "LLM_BASE_URL" IS_IN result.stderr OR "配置错误" IS_IN result.stderr
```

---

### 5.2 test_e2e_valid_env_import

| 属性 | 值 |
|------|-----|
| 目标 | 应用启动流程 |
| 场景 | 环境变量完整时正常导入 |
| 断言 | 导入成功，配置正确 |

```python
def test_e2e_valid_env_import(valid_env):
    """测试完整环境变量下正常启动"""
    # 在子进程中测试导入
    import subprocess
    import sys
    
    code = '''
import config
print(config.LLM_CONFIG.base_url)
print(config.LLM_CONFIG.model)
print(config.LLM_CONFIG.api_key[:10] + '***')
    '''
    
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "https://api.openai.com/v1" in result.stdout
    assert "gpt-4o" in result.stdout
```

**Pseudocode:**
```
TEST test_e2e_valid_env_import:
    code = "
        import config
        PRINT config.LLM_CONFIG.base_url
        PRINT config.LLM_CONFIG.model
        PRINT config.LLM_CONFIG.api_key[:10] + "***"
    "
    result = RUN_SUBPROCESS([python, "-c", code])
    ASSERT result.returncode EQUALS 0
    ASSERT "https://api.openai.com/v1" IS_IN result.stdout
    ASSERT "gpt-4o" IS_IN result.stdout
```

---

## 6. 测试执行

### 6.1 运行全部测试

```bash
# 运行所有测试
pytest

# 运行并显示详细输出
pytest -v

# 运行特定模块
pytest tests/test_config.py

# 运行特定测试
pytest tests/test_config.py::test_build_config_success

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 6.2 CI 配置示例

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=. --cov-report=xml
```

---

## 7. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-05-06 | 初始版本，定义完整测试策略和用例 |

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| [spec.md](spec.md) | 项目技术规范 |
| [requirement.md](requirement.md) | 功能与非功能需求 |
| [api.md](api.md) | API 设计与伪代码 |

---

*本文档由 Cue-Pro 项目维护，新增功能需同步补充测试用例。*