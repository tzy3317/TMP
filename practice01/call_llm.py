import os
import time
import json
import http.client
from urllib.parse import urlparse

# 读取.env文件
def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env = {}
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    return env

# 计算token数量（简单实现，实际项目中应使用tiktoken库）
def count_tokens(text):
    return len(text.split())

# 调用LLM API
def call_llm(prompt, env):
    # 从环境变量获取配置
    api_key = env.get('API_KEY')
    base_url = env.get('BASE_URL', 'https://api.openai.com/v1')
    model_name = env.get('MODEL_NAME', 'gpt-3.5-turbo')
    max_tokens = int(env.get('MAX_TOKENS', 2000))
    temperature = float(env.get('TEMPERATURE', 0.7))
    timeout = int(env.get('TIMEOUT', 30))
    
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    
    # 构建请求数据
    data = {
        'model': model_name,
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 创建连接
        if parsed_url.scheme == 'https':
            conn = http.client.HTTPSConnection(host, timeout=timeout)
        else:
            conn = http.client.HTTPConnection(host, timeout=timeout)
        
        # 发送请求
        conn.request('POST', path, body=json.dumps(data), headers=headers)
        
        # 获取响应
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        
        # 记录结束时间
        end_time = time.time()
        
        # 解析响应
        result = json.loads(response_data)
        
        if 'error' in result:
            print(f"API错误: {result['error']['message']}")
            return None, 0, 0, 0
        
        # 提取响应内容
        message = result['choices'][0]['message']['content']
        
        # 统计token消耗
        usage = result.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # 计算时间
        elapsed_time = end_time - start_time
        
        # 计算token/速度
        if elapsed_time > 0:
            tokens_per_second = total_tokens / elapsed_time
        else:
            tokens_per_second = 0
        
        return message, total_tokens, elapsed_time, tokens_per_second
        
    except Exception as e:
        print(f"请求错误: {str(e)}")
        end_time = time.time()
        return None, 0, end_time - start_time, 0
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    # 加载环境变量
    env = load_env()
    
    if not env.get('API_KEY'):
        print("错误: 请在.env文件中设置API_KEY")
        print("提示: 复制.env.example为.env并填写正确的API密钥")
        return
    
    # 测试提示词
    prompt = "请解释什么是人工智能，以及它的主要应用领域"
    
    print("正在调用LLM API...")
    print(f"使用模型: {env.get('MODEL_NAME', 'gpt-3.5-turbo')}")
    print(f"请求URL: {env.get('BASE_URL', 'https://api.openai.com/v1')}")
    print()
    
    # 调用LLM
    message, total_tokens, elapsed_time, tokens_per_second = call_llm(prompt, env)
    
    if message:
        print("=== 响应内容 ===")
        print(message)
        print()
    
    print("=== 统计信息 ===")
    print(f"总token消耗: {total_tokens}")
    print(f"请求耗时: {elapsed_time:.2f} 秒")
    print(f"Token速度: {tokens_per_second:.2f} tokens/秒")

if __name__ == "__main__":
    main()
