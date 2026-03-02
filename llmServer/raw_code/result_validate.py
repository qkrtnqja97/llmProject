# 자동 시각화
# ==========================================
# [5] Result Validation 노드
# ==========================================
def result_validate_node(state: AgentState) -> dict:
    """DB 실행 성공 후 결과 데이터 sanity check
    - 0건: 재시도 X, answer_node에서 '데이터 없음'으로 안내
    - 음수 매출 / 비정상 이상값: 재시도 O (SQL 로직 오류 가능성)
    """
    df = state.get("df")
    plan = state.get("query_plan", {})
    anomalies = []

    # 0건은 재시도 하지 않음 - answer_node가 "데이터 없음"으로 처리
    if df is None or len(df) == 0:
        return {"result_anomalies": []}

    # NULL 비율 과다 (80% 이상으로 기준 강화 - 50%는 너무 민감)
    for col in df.columns:
        null_ratio = df[col].isna().sum() / len(df)
        if null_ratio > 0.8:
            anomalies.append(f"'{col}' NULL {null_ratio:.0%} 초과.")

    # 음수 매출/수익 (비즈니스 규칙 위반 - 재시도 가치 있음)
    for col in df.columns:
        if any(
            k in col.lower()
            for k in ["revenue", "price", "cost", "profit", "amount", "매출", "수익"]
        ):
            if pd.api.types.is_numeric_dtype(df[col]):
                neg = (df[col] < 0).sum()
                if neg > 0:
                    anomalies.append(f"'{col}' 음수값 {neg}건 (비즈니스 규칙 위반).")

    # 비정상 이상값 (평균의 10000배 초과로 기준 완화)
    for col in df.select_dtypes(include="number").columns:
        mean_v = df[col].mean()
        if mean_v > 0:
            max_v = df[col].max()
            if max_v > mean_v * 10000:
                anomalies.append(f"'{col}' 최대값({max_v:,.0f}) 이상 감지.")

    if anomalies:
        logger.warning(f"Result Anomaly: {anomalies}")
        return {
            "result_anomalies": anomalies,
            "db_result": f"Error: 결과 이상 감지 - {' | '.join(anomalies)}",
            "error_history": state.get("error_history", []) + anomalies,
            "retry_count": state.get("retry_count", 0) + 1,
        }
    return {"result_anomalies": []}
