from flask import Flask, request, jsonify
import os, re
import requests, json
from urllib.parse import quote


app = Flask(__name__)

LOSTARK_API_KEY = os.environ.get("LOSTARK_API_KEY")
BASE_URL = "https://developer-lostark.game.onstove.com"

headers = {
    "accept": "application/json",
    "authorization": f"bearer {LOSTARK_API_KEY}"
}

#장비 툴팁 리로드
def parse_tooltip_effects(tooltip_str):
    try:
        tooltip = json.loads(tooltip_str)

        # 품질
        quality = 0
        element_001 = tooltip.get("Element_001", {})
        value = element_001.get("value", {})
        if isinstance(value, str):
            value = json.loads(value)
        if isinstance(value, dict):
            quality = int(value.get("qualityValue", 0))
        
        # 상급 재련
        refine_text = tooltip.get("Element_005", {}).get("value", "")
        refine_match = re.search(r">(\d{1,2})<", refine_text)
        refine = refine_match.group(1) + "단계" if refine_match else "-"

        # 초월
        transcend = tooltip.get("Element_010", {}).get("value", {}).get("Element_000", {}).get("topStr", "")
        transcend = re.sub(r"<.*?>", "", transcend).strip() if transcend else "-"

        # 엘릭서
        elixir_block = tooltip.get("Element_011", {}).get("value", {}).get("Element_000", {}).get("contentStr", {})
        elixirs = []
        for val in elixir_block.values():
            line = re.sub(r"<.*?>", "", val.get("contentStr", ""))
            if line:
                elixirs.append(line.strip())
        elixir = " / ".join(elixirs) if elixirs else "-"

        return quality, refine, elixir, transcend
    except Exception as e:
        print("Tooltip 파싱 오류:", e)
        return 0, "-", "-", "-"


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
        print("🧾 [장비 전체 응답 JSON] ↓↓↓")
        import json
        print(json.dumps(equip_data, indent=2, ensure_ascii=False))  # 한글 포함 이쁘게 출력

        if not equip_data:
            return jsonify({"message": f"'{name}'님의 장비 정보가 없습니다."})

        message = f"[{name}]님에 대한 장비 정보\n\n"
        total_quality = 0
        count = 0

        for item in equip_data:
            #아이템 고대랑 파츠 구분
            grade = item.get("Grade", "")
            part = item.get("Type", "")
            #아이템 품질/상급재련/엘릭서/초월 가져오기
            tooltip_str = item.get("Tooltip", "")

            quality, refine, elixir, transcend = parse_tooltip_effects(tooltip_str)
        
            #장비 이름 가져오기
            name = item.get("Name", "")


            message += f"[{grade} {part}] {name} / 품질 : {quality} / 상급재련 : {refine}\n"
            message += f" 🌿초월: {transcend}\n"
            if part != "무기":
                message += f" ⚗ 엘릭서: {elixir}\n\n"
            
            
           
                

           


            if part in["무기", "투구", "상의", "하의", "장갑", "어깨"]:
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
