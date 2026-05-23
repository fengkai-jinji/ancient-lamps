import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# AI对话API路由
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': '消息内容不能为空'}), 400
        
        # 使用DeepSeek API
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        url = 'https://api.deepseek.com/v1/chat/completions'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是智慧古灯助手，专注于解答关于古灯的历史、文化、设计和3D打印等方面的问题。请用友好、专业的语言回答用户的问题。'
                },
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if not response.ok:
            raise Exception(f'API error: {response.status}')
        
        data = response.json()
        return jsonify({'response': data['choices'][0]['message']['content']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 健康检查路由
@app.route('/')
def hello_world():
    return '古代精品灯具API服务运行中'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
