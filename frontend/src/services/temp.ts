// frontend/src/services/chatService.ts

// 나중에 진짜 백엔드 붙일 때 이 함수만 수정하면 됨!
export async function sendChatMessage(message: string): Promise<string> {
  console.log("💬 (MOCK) sendChatMessage:", message);

  // 응답 오는 척 딜레이
  await new Promise((resolve) => setTimeout(resolve, 700));

  const examples = [
    "지금은 프론트 전용 목업 모드입니다. 백엔드는 나중에 붙여도 돼요 😎",
    "이 메시지는 실제 AI가 아니라, 더미 응답이에요!",
    "UI 레이아웃 테스트 중이라면 이 정도면 충분합니다 👍",
  ];

  const random = examples[Math.floor(Math.random() * examples.length)];

  return random + `\n\n(사용자 입력: "${message.slice(0, 30)}...")`;
}