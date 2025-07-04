from dotenv import load_dotenv
load_dotenv()

import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
LOSTARK_API_KEY = os.environ.get("LOSTARK_API_KEY")

@app.route('/webhook', methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    user_message = req.get('userRequest', {}).get('utterance', '').strip()

    # 예: "닉네임 홍길동" 입력 시
    if user_message.startswith("닉네임 "):
        nickname = user_message.replace("닉네임 ", "").strip()
        url = f"https://developer-lostark.game.onstove.com/characters/{nickname}/siblings"
        headers = {
            "accept": "application/json",
            "authorization": f"bearer {LOSTARK_API_KEY}"
        }
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            data = res.json()
            character_list = [char['CharacterName'] for char in data]
            reply_text = f"{nickname}의 원정대 캐릭터: {', '.join(character_list)}"
        else:
            reply_text = f"⚠️ '{nickname}'에 대한 정보를 불러오지 못했습니다."
    else:
        reply_text = f"'{user_message}'에 대한 응답 준비 중이에요."

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {
                    "text": reply_text
                    }
                    }
            ]
        }
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
