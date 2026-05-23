import requests

# 测试根路径
print("测试根路径:")
try:
    response = requests.get('http://localhost:5000/')
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"错误: {e}")

# 测试AI对话API
print("\n测试AI对话API:")
try:
    response = requests.post('http://localhost:5000/api/ai/chat', json={'message': '你好，古灯助手'})
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 测试首页灯具API
print("\n测试首页灯具API:")
try:
    response = requests.get('http://localhost:5000/api/home')
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
except Exception as e:
    print(f"错误: {e}")
