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

    prefix_keywords = ["정보", "원정대", "부캐"]

    is_sibling = False
    name = raw_query

    for keyword in prefix_keywords:
        if raw_query.startswith(keyword + " "):
            name = raw_query[len(keyword):].strip()
            if keyword in ["원정대", "부캐"]:  # ✅ 원정대나 부캐일 때만 true
            is_sibling = True
            break

    if not name:
        return make_json({"error": "❗ 닉네임을 입력해주세요."}, 400)

    encoded_name = quote(name)
    if is_sibling:
         # ✅ 원정대 목록 URL
        url = f"https://developer-lostark.game.onstove.com/characters/{encoded_name}/siblings"
    else:
        # ✅ 단일 캐릭터 정보 URL
        url = f"https://developer-lostark.game.onstove.com/characters/{encoded_name}"


    headers = {
        "accept": "application/json",
        "authorization": f"bearer {LOSTARK_API_KEY}"
    }

    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        if is_sibling:
            # ✅ 원정대 목록 출력
            return make_json(get_sibling_message(name, data))
        else:
            # ✅ 캐릭터 상세 정보 출력
            return make_json(get_character_detail_message(data))
        
    except requests.exceptions.RequestException as e:
        return make_json({"error": f"❗ API 요청 오류: {str(e)}"}, 500)

    except ValueError as e:
        return make_json({"error": f"❗ JSON 파싱 실패: {str(e)}"}, 500)

@app.route("/equipment", methods=["GET"])
def character_equipment():
    name = request.args.get("name", "").strip()
    

    prefix_keywords = ["정보", "원정대", "부캐", "장비"]
    for prefix in prefix_keywords:
        if name.startswith(prefix + " "):
            name = name[len(prefix):].strip()
            break

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
           set_name = set_names[0]
           set_level = elixir_data[0].get("SetLevel", "2단계")
        else:
            set_name = "-"
            set_level = "-"
        message += f"엘릭서 세트 : {set_name} ({set_level})\n"


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

def get_sibling_message(rep_name, data):
    from collections import defaultdict

    server_dict = defaultdict(list)

    for char in data:
        server = char["ServerName"]
        server_dict[server].append(char)

    result = f"✳ '{rep_name}'의 원정대 캐릭터 목록:\n"
    for server, char_list in server_dict.items():
        result += f"\n- {server} 서버\n"
        # 평균 레벨 기준 내림차순 정렬
        sorted_chars = sorted(
            char_list,
            key=lambda c: float(c["ItemAvgLevel"].replace(",", "")),
            reverse=True
        )
        for c in sorted_chars:
            result += f"· {c['CharacterName']} (Lv. {c['ItemAvgLevel']})\n"

    return {"message": result}



def get_character_detail_message(data):
    return {
        "message": (
            f"📌 캐릭터명: {data['CharacterName']}\n"
            f"칭호: {data.get('Title', '-')}\n"
            f"서버: {data['ServerName']}\n"
            f"직업: {data['CharacterClassName']}\n"
            f"길드: {data.get('GuildName', '-')}\n"
            f"아이템 레벨: {data.get('ItemAvgLevel', '-')}\n"
            f"전투 레벨: {data.get('CharacterLevel', '-')}\n"
            f"영지: {data.get('TownName', '-')}\n"
            f"PVP 등급: {data.get('PvpGradeName', '-')}\n"
        )
    }


# ✅ JSON 한글 깨짐 방지용 헬퍼 함수
def make_json(data, status_code=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status_code
    return response

# ✅ 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
