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
    user_message = req.get('userRequest', {}).get('utterance', '').strip()

    # 기본 응답
    reply_text = f"'{user_message}'에 대한 응답을 준비 중이에요."

    # ✅ 도움말 명령어
    if user_message in ["도움말", "명령어", "help"]:
        reply_text = (
            "🧾 로아봇 명령어 안내\n\n"
            "1️⃣ 정보 [닉네임] - 캐릭터 원정대 목록 조회\n"
            "2️⃣ 장비 [닉네임] - 대표 캐릭터 장비 정보\n"
            "3️⃣ 특성 [닉네임] - 각인 및 스탯 정보\n"
            "4️⃣ 카드 [닉네임] - 카드 세트 정보\n"
            "5️⃣ 길드 [닉네임] - 길드 정보\n\n"
            "예: 정보 자라나라모리"
        )

    # ✅ 정보 명령어
    elif user_message.startswith("정보 "):
        parts = user_message.replace("정보", "").strip().split()

        if len(parts) == 0:
            reply_text = "⚠️ 캐릭터명을 입력해주세요. 예: 정보 닉네임"
        else:
            input_name = parts[0]
            encoded_nickname = quote(input_name)
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
                    found = any(char["CharacterName"] == input_name for char in data)

                    if found:
                        representative = data[0]["CharacterName"]
                        character_list = [char["CharacterName"] for char in data]
                        reply_text = (
                            f"🌟 '{representative}'의 원정대 캐릭터 목록:\n"
                            f"{', '.join(character_list)}"
                        )
                    else:
                        reply_text = f"⚠️ '{input_name}'은(는) 원정대에 포함되지 않은 캐릭터예요."
                except ValueError:
                    reply_text = f"⚠️ '{input_name}'의 JSON 데이터를 파싱하지 못했어요."
            else:
                reply_text = f"⚠️ '{input_name}'에 대한 정보를 찾을 수 없습니다. 상태코드: {res.status_code}"

    # ✅ 기타 입력 처리
    else:
        reply_text = "무엇을 원하시나요? 🤔\n명령어가 궁금하시다면 '도움말'이라고 입력해보세요!"

    return jsonify({
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
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
