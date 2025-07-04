from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ⚠️ 아래에 본인의 로스트아크 API 키 입력
LOA_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDA1ODM2NzMifQ.ToCVUsGvPh3HvhyFdanUOeBY0_X3TNdrQRMe-h9bx-thfLIxkx6vaQSLRagOsY9WXql20TgpoKcOeAITcUB3FX8SCatb14AzfMtmJ8tMQnaA_NliZNVjBG5gp0LdNtFGtr8TsajSgkWReR6paOdJPRuOsjxeFGdSJJPUOtFnsqDzxjW8uZiJNUP2sXIHhynR1iJFuXCKDJZgnCmnH66_lxzBonPmT5Kr95wUl6x1gI7ZkRoHufrserMX_Tu-uGx8v3LNpjB6aSgL7Nbyi6C9BUaSwYnHHruXuE7t46e2Ng6u8apswOUnDV-0I0FpodjxtiLOj3rzssvs407RwkM_uA"
HEADERS = {
    "accept": "application/json",
    "authorization": f"bearer {LOA_API_KEY}"
}

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    user_message = req.get("userRequest", {}).get("utterance", "").strip()

    # 로스트아크 API - 캐릭터 부캐 목록 조회
    url = f"https://developer-lostark.game.onstove.com/characters/{user_message}/siblings"
    res = requests.get(url, headers=HEADERS)

    if res.status_code == 200:
        data = res.json()
        sub_chars = [char["CharacterName"] for char in data]
        reply = f"'{user_message}'의 부캐 목록: " + ", ".join(sub_chars)
    else:
        reply = f"'{user_message}' 캐릭터 정보를 찾을 수 없습니다."

    # 카카오 i 오픈빌더 응답 형식
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": reply}}
            ]
        }
    })

if __name__ == "__main__":
    # 로컬에서는 5000 포트, 배포 환경에서는 자동 할당된 포트 사용
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
