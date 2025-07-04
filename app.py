from flask  import Flask, request, jsonify

import os

app = Flask(__name__)

from datetime import datetime

@app.route('/webhook', methods=['POST'])
def webhook():
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{now}] 🔔 Webhook 호출됨!")

    body = request.get_json(force=True, silent=True)
    print(f"[{now}] 📥 받은 요청:", body)

    user_message = body.get('userRequest', {}).get('utterance', '없음')
    print(f"[{now}] 🗨 사용자 메시지:", user_message)

    data = request.get_json()
    print("✅ 받은 요청:", data)

    user_message = data.get('userRequest', {}).get('utterance', '메시지 없음')
    print("✅ 사용자 메시지 수신:", user_message)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
