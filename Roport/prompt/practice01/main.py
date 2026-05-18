import sys


def main() -> None:
    print("=== Cue-Pro 启动 ===")
    print()

    from config import LLM_CONFIG
    from llm_client import LLMClient

    print("OK 配置加载成功")
    print(f"  服务商: {LLM_CONFIG.base_url}")
    print(f"  模型: {LLM_CONFIG.model}")
    print()

    client = LLMClient()
    print(">>> 发送测试消息...")
    response = client.chat("你好，请简单介绍一下自己。")
    print(f"<<< {response}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"程序异常: {e}")
        sys.exit(1)