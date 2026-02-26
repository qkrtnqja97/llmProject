# ==========================================
# 라우팅 보조: 데이터 관련 키워드 사전 감지
# ==========================================
DATA_KEYWORDS = [
    # 재고/제품
    "재고", "품목", "제품", "상품", "부품", "수량", "현재고", "재고량",
    # 매출/매입
    "매출", "매입", "판매", "구매", "주문", "발주",
    # 분석 동사
    "많은", "적은", "높은", "낮은", "최대", "최소", "평균", "합계", "총",
    "얼마", "몇", "뭐야", "뭐지", "뭔지", "알려줘", "보여줘", "조회",
    "순위", "랭킹", "비교", "분석", "추이", "현황", "통계",
    # 시간
    "이번달", "저번달", "지난달", "올해", "작년", "이번주", "최근",
    "지금", "현재", "오늘",
    # 공급사/판매처
    "공급사", "제조사", "업체", "거래처", "벤더",
]

TECH_SALES_KEYWORDS = [
    "스펙", "사양", "데이터시트", "datasheet", "핀맵", "pinout",
    "대체품", "호환", "equivalent", "alternative",
    "납기", "리드타임", "재고확인", "EOL", "단종",
    "온도범위", "전압", "전류", "패키지", "풋프린트",
    "RoHS", "AEC-Q", "인증", "규격",
    "추천", "제안", "견적",
]

def is_data_question(q: str) -> bool:
    return any(kw in q for kw in DATA_KEYWORDS)

def is_tech_sales(q: str) -> bool:
    return any(kw in q for kw in TECH_SALES_KEYWORDS)

def get_work_context_summary() -> str:
    """최근 업무 대화 맥락 요약 (분류기에 주입용)"""
    work_ctx = st.session_state.get("work_context", [])
    if not work_ctx:
        return ""
    # 최근 4개 메시지만 사용
    recent = work_ctx[-4:]
    lines = []
    for m in recent:
        role = "사용자" if m["role"] == "user" else "AI"
        lines.append(f"{role}: {m['content'][:80]}")
    return "\n".join(lines)



def router_node(state: AgentState):
    q = state["question"]

    # ── 1차: 데이터 키워드 → 즉시 INVENTORY ────────────────────
    if is_data_question(q):
        logger.info(f"라우터: 데이터 키워드 → INVENTORY | {q}")
        return {"intent": "INVENTORY"}

    # ── 2차: 테크니컬 키워드 → 즉시 TECH_SALES ─────────────────
    if is_tech_sales(q):
        logger.info(f"라우터: 기술영업 키워드 → TECH_SALES | {q}")
        return {"intent": "TECH_SALES"}

    # ── 3차: LLM 분류 (업무 맥락 주입으로 후속질문 정확도 향상) ──
    work_ctx = get_work_context_summary()
    ctx_section = f"\n[직전 업무 대화 맥락]\n{work_ctx}" if work_ctx else ""

    prompt = PromptTemplate.from_template("""당신은 전자부품 수입 유통 회사의 AI 챗봇 분류기입니다.
    아래 질문을 세 가지 중 하나로만 분류하세요.

    INVENTORY  : 재고/매출/매입/수익/품목/고객사/제조사 등 데이터 조회·분석 요청
    TECH_SALES : 부품 스펙·사양·대체품·호환성·납기·기술 문의 등 테크니컬 세일즈 요청
    CHIT_CHAT  : 업무와 전혀 무관한 일상 대화{ctx_section}

    [중요] 직전 업무 대화가 있고 질문이 짧거나 확인성("그래서", "3월은?", "맞아?", "왜?", "다시")이면
    → 직전 업무와 같은 분류로 처리하세요.

    [INVENTORY 예시]
    - "이번달 매출 얼마야" → INVENTORY
    - "재고 현황" → INVENTORY
    - "3월은?" (직전: 매출 조회) → INVENTORY
    - "맞아?" (직전: 데이터 응답) → INVENTORY

    [TECH_SALES 예시]
    - "BCM5650의 대체품 있어?" → TECH_SALES
    - "이 부품 납기 얼마나 걸려?" → TECH_SALES

    [CHIT_CHAT 예시]
    - "안녕" → CHIT_CHAT
    - "밥 뭐 먹지" → CHIT_CHAT
    - "오늘 날씨 어때" → CHIT_CHAT

    질문: {q}
    분류:""")

    try:
        raw = (prompt | llm | StrOutputParser()).invoke({"q": q, "ctx_section": ctx_section}).strip().upper()
        if "INVENTORY" in raw:
            result = "INVENTORY"
        elif "TECH_SALES" in raw or "TECH" in raw:
            result = "TECH_SALES"
        else:
            result = "CHIT_CHAT"
    except Exception:
        logger.exception("라우터 LLM 실패 → INVENTORY 폴백")
        result = "INVENTORY"

    logger.info(f"라우터: LLM 분류={result} | {q}")
    return {"intent": result}