const express = require("express");
const axios = require("axios");
require("dotenv").config();

const app = express();
app.use(express.json());

const LOSTARK_API_KEY = process.env.LOSTARK_API_KEY;

app.post("/webhook", async (req, res) => {
  const userMessage = req.body.userRequest?.utterance?.trim() || "";

  let replyText = `'${userMessage}'에 대한 응답을 준비 중이에요.`;

  // ✅ 1. 도움말 명령어
  if (["도움말", "명령어", "help"].includes(userMessage)) {
    replyText =
      "🧾 로아봇 명령어 안내\n\n" +
      "1️⃣ 정보 [닉네임] - 캐릭터 원정대 목록 조회\n" +
      "2️⃣ 장비 [닉네임] - 대표 캐릭터 장비 정보\n" +
      "3️⃣ 특성 [닉네임] - 각인 및 스탯 정보\n" +
      "4️⃣ 카드 [닉네임] - 카드 세트 정보\n" +
      "5️⃣ 길드 [닉네임] - 길드 정보\n\n" +
      "예: 정보 자라나라모리";
  }

  // ✅ 2. 정보 명령어
  else if (userMessage.startsWith("정보 ")) {
    const parts = userMessage.replace("정보", "").trim().split(" ");

    if (parts.length === 0 || !parts[0]) {
      replyText = "⚠️ 캐릭터명을 입력해주세요. 예: 정보 닉네임";
    } else {
      const inputName = parts[0];
      const encodedName = encodeURIComponent(inputName);
      const url = `https://developer-lostark.game.onstove.com/characters/${encodedName}/siblings`;

      try {
        const response = await axios.get(url, {
          headers: {
            Authorization: `bearer ${LOSTARK_API_KEY}`,
            Accept: "application/json",
          },
        });

        const data = response.data;
        const found = data.some((char) => char.CharacterName === inputName);

        if (found) {
          const representative = data[0].CharacterName;
          const characterList = data.map(
            (char) =>
              `${char.CharacterName} (${char.CharacterClassName}, ${char.ItemAvgLevel})`
          );
          replyText = `🌟 '${representative}'의 원정대 캐릭터 목록:\n- ` + characterList.join("\n- ");
        } else {
          replyText = `⚠️ '${inputName}'은(는) 원정대에 포함되지 않은 캐릭터예요.`;
        }
      } catch (error) {
        console.error("❌ API 오류:", error.message);
        replyText = `⚠️ '${inputName}'에 대한 정보를 불러오는 데 실패했어요.`;
      }
    }
  }

  // ✅ 3. 그 외 입력 처리
  else {
    replyText = "무엇을 원하시나요? 🤔\n'도움말'이라고 입력해보세요!";
  }

  // ✅ 카카오톡 응답
  res.json({
    version: "2.0",
    template: {
      outputs: [
        {
          simpleText: {
            text: replyText,
          },
        },
      ],
    },
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 서버 실행 중! 포트: ${PORT}`);
});
