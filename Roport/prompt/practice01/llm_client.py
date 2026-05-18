import http.client
import json
import time
from typing import Generator
from urllib.parse import urlparse
from dotenv import load_dotenv

# 加载项目根目录 .env 文件
load_dotenv()

from config import LLMConfig, LLM_CONFIG

_SYSTEM_PROMPT = "You are a helpful assistant."

class LLMClient:
    """LLM 客户端封装类（标准HTTP库实现 + 耗时/Token统计）"""
    _config: LLMConfig

    def __init__(self, config: LLMConfig | None = None) -> None:
        self._config = config or LLM_CONFIG

    def chat(self, message: str, system_prompt: str | None = None) -> str:
        system_prompt = system_prompt or _SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        start_time = time.time()
        parsed = urlparse(self._config.base_url)
        scheme = parsed.scheme
        host = parsed.hostname
        port = parsed.port

        # 固定正确接口路径
        api_path = "/v1/chat/completions"

        # 创建连接
        if scheme == "https":
            conn = http.client.HTTPSConnection(host, port, timeout=self._config.timeout)
        elif scheme == "http":
            conn = http.client.HTTPConnection(host, port, timeout=self._config.timeout)
        else:
            raise ValueError("base_url 必须以 http:// 或 https:// 开头")

        payload = json.dumps({
            "model": self._config.model,
            "messages": messages,
            "max_tokens": self._config.max_tokens,
            "temperature": self._config.temperature,
            "top_p": self._config.top_p,
            "stream": False
        })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config.api_key}"
        }

        # 发送请求
        conn.request("POST", api_path, payload, headers)
        resp = conn.getresponse()
        status_code = resp.status
        data = resp.read().decode()
        result = json.loads(data)

        # 统计信息
        duration = time.time() - start_time
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        speed = completion_tokens / duration if duration > 0 else 0

        print("\n====== LLM 请求统计 ======")
        print(f"耗时：{duration:.2f}s")
        print(f"输入token：{prompt_tokens}")
        print(f"输出token：{completion_tokens}")
        print(f"总token：{total_tokens}")
        print(f"速度：{speed:.2f} token/s")
        print("==========================\n")

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return f"请求失败：{result}"

    def chat_stream(self, message: str, system_prompt: str | None = None) -> Generator[str, None, None]:
        system_prompt = system_prompt or _SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        start_time = time.time()
        completion_tokens = 0

        parsed = urlparse(self._config.base_url)
        scheme = parsed.scheme
        host = parsed.hostname
        port = parsed.port
        api_path = "/v1/chat/completions"

        if scheme == "https":
            conn = http.client.HTTPSConnection(host, port, timeout=self._config.timeout)
        elif scheme == "http":
            conn = http.client.HTTPConnection(host, port, timeout=self._config.timeout)
        else:
            raise ValueError("base_url 必须以 http:// 或 https:// 开头")

        payload = json.dumps({
            "model": self._config.model,
            "messages": messages,
            "max_tokens": self._config.max_tokens,
            "temperature": self._config.temperature,
            "top_p": self._config.top_p,
            "stream": True
        })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._config.api_key}"
        }

        conn.request("POST", api_path, payload, headers)
        resp = conn.getresponse()

        for line in resp:
            line = line.decode().strip()
            if not line or not line.startswith("data: "):
                continue
            data = line.replace("data: ", "")
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    completion_tokens += 1
                    yield delta
            except:
                continue

        duration = time.time() - start_time
        speed = completion_tokens / duration if duration > 0 else 0
        print(f"\n流式耗时：{duration:.2f}s  输出Token：{completion_tokens}  速度：{speed:.2f} token/s")


# ====================== 交互式自由提问（你自己输入问题）======================
if __name__ == "__main__":
    llm = LLMClient()
    print("=" * 50)
    print("🎯 LLM 交互式对话工具（输入 exit 退出）")
    print("=" * 50)

    while True:
        user_input = input("\n🙋 你的问题：")
        if user_input.strip().lower() == "exit":
            print("👋 退出对话！")
            break
        if not user_input.strip():
            print("⚠️  请输入有效问题！")
            continue

        # 流式输出（逐字显示，体验更好）
        print("\�🤖 AI 回答：", end="", flush=True)
        for chunk in llm.chat_stream(user_input):
            print(chunk, end="", flush=True)
        print()