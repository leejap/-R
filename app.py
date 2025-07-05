from flask import Flask, request, make_response
from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote
import json
from collections import defaultdict  


# .env 파일에서 API 키 불러오기
load_dotenv()

app = Flask(__name__)
LOSTARK_API_KEY = os.environ.get("LOSTARK_API_KEY")  # .env 파일에 있어야 함

@app.route("/character", methods=["GET"])
def character_info():
    raw_query = request.args.get("name", "").strip()

    prefix_keywords = ["원정대", "부캐"]

    for keyword in prefix_keywords:
        if raw_query.startswith(keyword + " "):
            name = raw_query[len(keyword):].strip()
            break
    else:
        name = raw_query
    if not name:
        return make_json({"error": "❗ 닉네임을 입력해주세요."}, 400)

    encoded_name = quote(name)
    url = f"https://developer-lostark.game.onstove.com/characters/{encoded_name}/siblings"

    headers = {
        "accept": "application/json",
        "authorization": f"bearer {LOSTARK_API_KEY}"
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return make_json({"error": f"❗ '{name}'을(를) 찾을 수 없습니다."}, 404)

    try:
        data = res.json()
        found = any(char["CharacterName"] == name for char in data)

        if found:
            representative = name  # 사용자가 입력한 캐릭터명을 기준으로 표시

            server_dict = defaultdict(list)
            for char in data:
                server = char["ServerName"]
                cname = char["CharacterName"]
                server_dict[server].append(cname)

            character_list = []

            for server in sorted(server_dict.keys()):
                character_list.append(f"- {server} 서버")
                
                sorted_characters = sorted(
                server_dict[server],
                key=lambda cname : float(
                    next(
                       (c.get("ItemAvgLevel", "0") for c in data if c["CharacterName"] == cname),
                        "0"
                    ).replace(",", "")
                ),
                reverse=True  
            )
                
                
                for cname in sorted_characters:
                    char_info = next((c for c in data if c["CharacterName"] == cname), None)
                    item_level = (
                        char_info.get("ItemAvgLevel","알 수 없음") 
                        if char_info and isinstance(char_info, dict)
                        else "알 수 없음"
                    )
                    character_list.append(f"  · {cname} (Lv. {item_level})")

            print(f"[디버깅] char_info for {cname}: {char_info}")
           

            message = f"🌟 '{representative}'의 원정대 캐릭터 목록:\n" + "\n".join(character_list)
            return make_json({
                "name": representative,
                "characters": character_list,
                "message": message
            })
        else:
            return make_json({"error": f"❗ '{name}'은(는) 원정대에 포함되지 않은 캐릭터입니다."}, 404)

    except Exception as e:
        return make_json({"error": f"❗ JSON 파싱 실패: {str(e)}"}, 500)

@app.route("/equipment", methods=["GET"])
def character_equipment():
    name = request.args.get("name", "").strip()
    if not name:
        return make_json({"error": "❗ 닉네임을 입력해주세요."}, 400)

    encoded_name = quote(name)
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {LOSTARK_API_KEY}"
    }

    try:
        # 장비 정보 가져오기
        equip_url = f"https://developer-lostark.game.onstove.com/characters/{encoded_name}/equipment"
        equip_res = requests.get(equip_url, headers=headers)
        equip_data = equip_res.json()

        # 엘릭서 정보 가져오기
        elixir_url = f"https://developer-lostark.game.onstove.com/characters/{encoded_name}/elixirs"
        elixir_res = requests.get(elixir_url, headers=headers)
        elixir_data = elixir_res.json()

        # 초월 정보 가져오기
        transcend_url = f"https://developer-lostark.game.onstove.com/characters/{encoded_name}/transcendence"
        transcend_res = requests.get(transcend_url, headers=headers)
        transcend_data = transcend_res.json()

        # 👉 여기서 각각 포맷팅한 후 message 조립
        message = f"[{name}]님에 대한 장비 정보\n\n"

        # 1. 장비
        message += "<장비>\n"
        qualities = []
        for item in equip_data:
            if item["Type"] in ["무기", "투구", "상의", "하의", "장갑", "어깨"]:
                message += f"[{item['Grade']} {item['Type']}] +{item['Enhancement']}  / 품질 : {item['Quality']} / 상급재련 : {item['Tiers']}단계\n"
                qualities.append(int(item['Quality']))

        if qualities:
            avg_quality = sum(qualities) // len(qualities)
            message += f"평균 품질 : {avg_quality}\n"

        # 2. 엘릭서
        message += "\n<엘릭서 현황>\n"
        total_elixir = 0
        set_names = []
        for e in elixir_data:
            message += f"{e['Slot']} [{e['Name']}] {e['EffectType']}  Lv.{e['Level']}\n"
            total_elixir += int(e['Level'])
            if e['SetName']:
                set_names.append(e['SetName'])
        message += f"\n엘릭서 합계 : {total_elixir}\n"
        if set_names:
            message += f"엘릭서 세트 : {set_names[0]} (2단계)\n"  # 예시

        # 3. 초월
        message += "\n<초월 현황>\n"
        total_trans = 0
        for t in transcend_data:
            message += f"{t['Type']} 슬롯 효과 [초월] {t['Level']}단계 {t['Grade']}등급\n"
            total_trans += int(t['Grade'])
        message += f"초월합계 : {total_trans}\n"

        return make_json({"message": message})

    except Exception as e:
        return make_json({"error": f"❗ 서버 오류: {str(e)}"}, 500)

# ✅ JSON 한글 깨짐 방지용 헬퍼 함수
def make_json(data, status_code=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status_code
    return response

# ✅ 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
