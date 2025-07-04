from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    now = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{now}] 🔔 Webhook 호출됨!", flush=True)

    body = request.get_json(force=True, silent=True)
    print(f"[{now}] 📥 받은 요청 바디: {body}", flush=True)

    user_message = body.get("userRequest", {}).get("utterance", "없음")
    print(f"[{now}] 💬 사용자 메시지: {user_message}", flush=True)

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
