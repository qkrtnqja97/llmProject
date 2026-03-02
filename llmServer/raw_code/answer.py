# 최종 답변 생성
def answer_node(state: AgentState):
    if state.get("intent") == "CHIT_CHAT":
        return {"db_result": "__CHIT_CHAT__"}

    if state.get("intent") == "TECH_SALES":
        q = state.get("question", "")
        work_ctx = st.session_state.get("work_context", [])
        ctx_lines = [
            f"{'사용자' if m['role']=='user' else 'AI'}: {m['content'][:100]}"
            for m in work_ctx[-4:]
        ]
        ctx_str = "\n".join(ctx_lines) if ctx_lines else "없음"
        prompt = PromptTemplate.from_template(
            """당신은 전자부품 수입 유통 전문 테크니컬 세일즈 AI입니다.
전자부품 스펙, 대체품, 납기, 호환성, 기술 문의에 전문적으로 답변하세요.

[직전 업무 대화 맥락]
{ctx}

[질문]
{q}

[답변 규칙]
- 확실하지 않은 스펙은 "데이터시트 확인 필요"로 명시
- 대체품 추천 시 반드시 호환성 주의사항 포함
- 간결하고 전문적으로 답변"""
        )
        try:
            ans = (prompt | llm | StrOutputParser()).invoke({"q": q, "ctx": ctx_str})
        except Exception:
            ans = "테크니컬 문의 처리 중 오류가 발생했습니다."
        return {"db_result": ans}

    db_res = state.get("db_result", "")
    if "Error" in db_res:
        return {"db_result": f"❌ 분석 실패: {db_res}"}

    df = state.get("df")
    if df is None or df.empty:
        return {"db_result": "🔍 해당 조건의 데이터가 존재하지 않습니다."}

    # ==========================================
    # [수정] 환각 방지 및 데이터 해석 강화 프롬프트
    # ==========================================
    prompt = PromptTemplate.from_template(
        """당신은 전자부품 재고 데이터 분석가입니다.
아래 제공된 [실제 데이터] 테이블은 DB에서 갓 뽑아온 '진실'입니다.
테이블에 단 한 줄이라도 데이터가 있다면, 정보를 확인할 수 없다는 답변은 '오답'이자 '거짓말'입니다.

[질문]
{q}

[실제 데이터]
{d}

[데이터 메타 정보]
{meta}

[답변 절대 지침] ← 위반 시 업무 태만
1. 데이터 맹신: 테이블에 'IC'라고 적혀 있으면 파나소닉 제품 종류는 'IC'인 것입니다. 데이터가 부족하다고 변명하지 마세요.
2. 부정 답변 금지: "정보가 포함되어 있지 않습니다", "확인할 수 없습니다", "알 수 없습니다" 같은 표현을 절대 사용하지 마세요.
3. 팩트 기반 요약: 테이블의 내용을 그대로 읽어서 2~3문장으로 답변하세요.
4. 마크다운 표 생성 금지: 텍스트로만 설명하세요. 화면에 이미 표가 그려져 있습니다.

[단위 규칙]
- 금액: 원(KRW) 단위, 반올림 정수 표기 (예: 1,200,000,000원)
- 수량: 개 단위 표기

답변:"""
    )

    row_count = len(df)
    # [기능] 데이터가 있음에도 헛소리하는 것을 막기 위해 meta 정보에 강한 어조 추가
    meta_info = f"현재 총 {row_count}행의 데이터가 정상 조회되었습니다. 이 데이터를 기반으로 즉시 답변하세요. 데이터 부재를 핑계로 답변을 거부하지 마세요."

    try:
        ans = (prompt | llm | StrOutputParser()).invoke(
            {"q": state["question"], "d": df.head(10).to_string(), "meta": meta_info}
        )
    except Exception as e:
        ans = f"답변 생성 중 오류가 발생했습니다: {str(e)}"

    return {"db_result": ans}
