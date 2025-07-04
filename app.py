from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 요청 데이터 수신
    body = request.get_json(force=True, silent=True)
    print(f"[{now}] 🔔 Webhook 호출됨")
    print(f"[{now}] 📥 받은 요청: {body}")

    # 사용자 발화 추출
    user_message = body.get('userRequest', {}).get('utterance', '없음')
    print(f"[{now}] 🗨 사용자 메시지: {user_message}")

    # 카카오 i 오픈빌더 응답 형식
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"당신이 보낸 메시지: {user_message}"
                    }
                }
            ]
        }
    }

    return jsonify(response)

# Railway가 사용하는 포트 환경변수에 맞춰 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
