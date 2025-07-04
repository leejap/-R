from flask import Flask, request, Response
from dotenv import load_dotenv
import os
import requests
import json

# .env 파일 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# LostArk API Key 불러오기
LOSTARK_API_KEY = os.environ.get("LOSTARK_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    user_message = req.get('userRequest', {}).get('utterance', '').strip()

    # 닉네임으로 시작하는 경우 처리
    if user_message.startswith("닉네임"):
        nickname = user_message.replace("닉네임", "").strip()
        url = f"https://developer-lostark.game.onstove.com/characters/{nickname}/siblings"

        headers = {
            "accept": "application/json",
            "authorization": f"bearer {LOSTARK_API_KEY}"
        }

        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            data = res.json()
            character_list = [char['CharacterName'] for char in data]
            reply_text = f"🌟 '{nickname}'의 원정대 캐릭터 목록: {', '.join(character_list)}"
        else:
            reply_text = f"⚠️ '{nickname}'에 대한 정보를 불러오지 못했습니다."
    else:
        reply_text = f"'{user_message}'에 대한 응답 준비 중이에요."

    # 카카오 스킬 응답 JSON 생성
    response_body = {
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

    # 한글 깨짐 방지를 위한 Response 객체 사용
    return Response(
        json.dumps(response_body, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )

# Railway 호환을 위한 run 설정
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
