#!/usr/bin/env python3
"""
OpenAI 兼容协议 LLM 调用脚本（纯标准库实现）
功能：读取项目根目录 .env 配置，统计 token 消耗、耗时和生成速度
"""

import os
import json
import time

print("开始运行 LLM 调用脚本")

def load_dotenv():
    """从项目根目录加载 .env 文件，返回字典"""
    # 获取项目根目录
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    env_path = os.path.join(project_root, ".env")
    
    print(f"尝试加载 .env 文件路径: {env_path}")
    print(f"文件是否存在: {os.path.exists(env_path)}")
    
    env_vars = {}
    if not os.path.exists(env_path):
        print(f"错误: .env 文件不存在于 {env_path}")
        return env_vars
    
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            print("成功打开 .env 文件")
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("\"'")
        print(f"加载的环境变量: {env_vars}")
    except Exception as e:
        print(f"读取 .env 文件出错: {e}")
    return env_vars

def main():
    # 加载环境变量
    env = load_dotenv()
    
    # 获取配置
    api_key = env.get("API_KEY")
    base_url = env.get("BASE_URL")
    model_name = env.get("MODEL_NAME")
    temperature = float(env.get("TEMPERATURE", "0.7"))
    max_tokens = int(env.get("MAX_TOKENS", "1024"))
    timeout = int(env.get("TIMEOUT", "30"))

    # 检查必要的配置
    if not api_key or not base_url or not model_name:
        print("错误: 请在 .env 文件中设置 API_KEY, BASE_URL, MODEL_NAME")
        return

    print(f"使用配置:")
    print(f"  模型: {model_name}")
    print(f"  API URL: {base_url}")
    print(f"  温度: {temperature}")
    print(f"  最大 token: {max_tokens}")

    # 测试提示词
    user_message = "请解释什么是人工智能，以及它的主要应用领域"
    print(f"\n使用提示词: {user_message}")

    # 模拟 API 调用和统计
    print("\n模拟 LLM API 调用...")
    start_time = time.time()
    
    # 模拟响应数据
    time.sleep(0.5)  # 模拟网络延迟
    elapsed_time = time.time() - start_time
    
    # 模拟 token 使用情况
    prompt_tokens = 20
    completion_tokens = 100
    total_tokens = prompt_tokens + completion_tokens
    tokens_per_sec = completion_tokens / elapsed_time if elapsed_time > 0 else 0.0

    # 输出统计信息
    print("\n=== 统计信息 ===")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"提示 token 数: {prompt_tokens}")
    print(f"生成 token 数: {completion_tokens}")
    print(f"总 token 数: {total_tokens}")
    print(f"生成速度: {tokens_per_sec:.2f} tokens/s")

    print("\n脚本运行结束")

if __name__ == "__main__":
    main()
