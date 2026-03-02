workflow = StateGraph(AgentState)

# 노드 등록
workflow.add_node("refine", entity_linking_node)
workflow.add_node("router", router_node)
workflow.add_node("sql_gen", generate_sql_node)
workflow.add_node("db_exec", execute_db_node)
workflow.add_node("result_validate", result_validate_node)
workflow.add_node("visual", visualize_node)
workflow.add_node("answer", answer_node)

workflow.set_entry_point("refine")
workflow.add_edge("refine", "router")


def route_by_intent(state):
    intent = state.get("intent", "INVENTORY")
    if intent in ("CHIT_CHAT", "TECH_SALES"):
        return "answer"
    return "sql_gen"  # INVENTORY → 바로 sql_gen


workflow.add_conditional_edges(
    "router", route_by_intent, {"answer": "answer", "sql_gen": "sql_gen"}
)

# sql_gen → db_exec (재시도 포함)
workflow.add_edge("sql_gen", "db_exec")
workflow.add_conditional_edges(
    "db_exec", should_retry, {"retry": "sql_gen", "success": "result_validate"}
)

# result_validate → 이상없으면 visual, 이상있으면 sql_gen 재시도
workflow.add_conditional_edges(
    "result_validate", should_retry_result, {"retry": "sql_gen", "visual": "visual"}
)

workflow.add_edge("visual", "answer")
workflow.add_edge("answer", END)
app_agent = workflow.compile()




# ==========================================
# 3. 그래프 조립
# ==========================================
# ✅ [#7] retry_count 기반 이중 재시도 제한
def should_retry(state: AgentState) -> str:
    has_error = "Error" in state.get("db_result", "")
    under_limit = state.get("retry_count", 0) < MAX_RETRY_COUNT
    if has_error and under_limit:
        return "retry"
    return "success"
  
  
  
  def should_retry_result(state: AgentState) -> str:
    if state.get("result_anomalies") and state.get("retry_count", 0) < MAX_RETRY_COUNT:
        return "retry"
    return "visual"
  


# ==========================================
# 2. 에이전트 노드 정의 (자가 치유 포함)
# ==========================================
class AgentState(TypedDict, total=False):
    # ── 기존 ──────────────────────────────────────────
    question: str
    refined_question: str
    synonym_hint: str
    intent: str
    sql_query: str
    db_result: any
    df: pd.DataFrame
    chart_info: Dict
    error_history: List[str]
    retry_count: int

    # ── [1] Query Planner ─────────────────────────────
    query_plan: Dict  # 구조화된 쿼리 계획 JSON

    # ── [3] Dynamic Schema ────────────────────────────
    selected_schema: str  # 선택된 테이블/컬럼 스키마

    # ── [4] Static Validator ──────────────────────────
    validation_errors: List[str]
    retry_strategy: str  # column_missing/table_missing/syntax/timeout/logic

    # ── [5] Result Validator ──────────────────────────
    result_anomalies: List[str]

    # ── [8] 구조화 메모리 ──────────────────────────────
    structured_memory: Dict  # last_metric/last_product/last_date_range 등

    # ── [9] 캐시 ──────────────────────────────────────
    cache_hit: bool
    cache_key: str

    # ── [10] Explainability ───────────────────────────
    explain_meta: Dict  # sql_used/filters_applied/aggregations 등
