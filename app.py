from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote

load_dotenv()

app = Flask(__name__)
LOSTARK_API_KEY = os.environ.get("LOSTARK_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    user_message = req.get('userRequest', {}).get('utterance', '')

    # 기본 응답 텍스트
    reply_text = f"'{user_message}'에 대한 응답을 준비 중이에요."

    if user_message.startswith("정보 ",):
        nickname = user_message.replace("정보 ", "").strip()
        encoded_nickname = quote(nickname)
        url = f"https://developer-lostark.game.onstove.com/characters/{encoded_nickname}/siblings"

        headers = {
             "accept": "application/json",
             "authorization": f"bearer {LOSTARK_API_KEY}"
             }

        res = requests.get(url, headers=headers)
        print(f"응답 코드: {res.status_code}")
        print(f"응답 내용: {res.text}")
        print(f"요청 URL: {url}")

        
  
        if res.status_code == 200:
            try:
                data = res.json()
                character_list = [char['CharacterName'] for char in data]
                reply_text = f"🌟 '{nickname}'의 원정대 캐릭터 목록: {', '.join(character_list)}"
            except ValueError:
                reply_text = f"⚠️ '{nickname}'의 JSON 데이터를 불러오는 데 실패했습니다."
        else:
            reply_text = f"⚠️ '{nickname}'에 대한 정보를 찾을 수 없습니다. 상태코드: {res.status_code}"

    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": reply_text
                    }
                }
            ]
        }
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
