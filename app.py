from flask import Flask, request, jsonify
import os
import requests
from urllib.parse import quote

app = Flask(__name__)

LOSTARK_API_KEY = os.environ.get("LOSTARK_API_KEY")
BASE_URL = "https://developer-lostark.game.onstove.com"

headers = {
    "accept": "application/json",
    "authorization": f"bearer {LOSTARK_API_KEY}"
}


@app.route("/character", methods=["GET"])
def character_info():
    try:
        raw_query = request.args.get("name", "").strip()
        if not raw_query:
            return jsonify({"error": "❗닉네임을 입력해주세요."}), 400

        # 접두어 필터링
        prefixes = ["정보", "원정대", "부캐"]
        name = raw_query
        for prefix in prefixes:
            if raw_query.startswith(prefix + " "):
                name = raw_query[len(prefix):].strip()
                break

        encoded_name = quote(name)
        url = f"{BASE_URL}/characters/{encoded_name}/siblings"
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return jsonify({"error": f"❗{name}님의 원정대 정보를 불러올 수 없습니다."}), 404

        data = res.json()
        if not data:
            return jsonify({"message": f"'{name}'님의 원정대에 등록된 캐릭터가 없습니다."})

        # ✅ 원정대 캐릭터 리스트 포맷팅
        message = f"✨ '{name}'의 원정대 캐릭터 목록:\n"
        prev_server = None
        for char in data:
            server = char["ServerName"]
            if server != prev_server:
                message += f"\n- {server} 서버\n"
                prev_server = server
            message += f"· {char['CharacterName']} (Lv. {char['ItemAvgLevel']})\n"

        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"error": f"⚠️ 서버 오류: {str(e)}"}), 500


@app.route("/equipment", methods=["GET"])
def character_equipment():
    try:
        raw_query = request.args.get("name", "").strip()
        if not raw_query:
            return jsonify({"error": "❗닉네임을 입력해주세요."}), 400

        name = raw_query.replace("장비", "").strip()
        encoded_name = quote(name)

        url = f"{BASE_URL}/armories/characters/{encoded_name}/equipment"
        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return jsonify({"error": f"❗{name}님의 장비 정보를 불러올 수 없습니다."}), 404

        equip_data = res.json()
        if not equip_data:
            return jsonify({"message": f"'{name}'님의 장비 정보가 없습니다."})

        message = f"[{name}]님에 대한 장비 정보\n\n"
        total_quality = 0
        count = 0

        for item in equip_data:
            grade = item.get("Grade", "")
            part = item.get("Type", "")
            value = item.get("enhancement", "")
            quality = item.get("qualityValue",  )
            refine = item.get("TinkerLevel", "10단계")
            item_name = item.get("Name", "")
            # 무기, 방어구, 악세등 +강화 숫자 추출
            if "+" in item_name:
                value = "+" + item_name.split("+")[1].split()[0]


            message += f"[{grade} {part}] +{value} / 품질 : {quality} / 상급재련 : {refine}\n"

            if "무기" in part or "투구" in part or "상의" in part or "하의" in part or "장갑" in part or "어깨" in part:
                total_quality += quality
                count += 1
                
        if count:
            avg_quality = round(total_quality / count)
            message += f"\n평균 품질 : {avg_quality}\n"

        # ✅ 이어서 엘릭서/초월 출력 (원하는 경우 별도 API로 호출 필요)

        return jsonify({"message": message})

    except Exception as e:
        return jsonify({"error": f"⚠️ 서버 오류: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
