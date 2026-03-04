# -*- coding: utf-8 -*-
"""
메인 Streamlit 애플리케이션
구조화된 api_llm 모듈을 사용하여 통합
"""

import os
import sys
import logging
import uuid
import time
from typing import Optional, Dict, List
from pathlib import Path

# ==========================================
# 경로 설정 (모듈 import 경로 수정)
# ==========================================
# Streamlit 또는 Python 직접 실행 시 모두 작동하도록
# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent  # llmProject 루트
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from langgraph.graph import StateGraph, END

# ==========================================
# 데이터베이스 자동 초기화 (맨 처음 실행)
# ==========================================
from api_llm.db_init import initialize_databases
db_resources = initialize_databases()  # 앱 시작 시 PostgreSQL + ChromaDB 자동 연결

# 패키지 임포트
from api_llm.config import (
    LOGGING_CONFIG, DATABASE_CONFIG, SQL_CONFIG,
    CACHE_CONFIG, API_CONFIG, SYSTEM_CONSTANTS, DATABASE_URL,
)
from api_llm.log_config.logger_config import setup_logging, get_logger

# 모듈 임포트
from api_llm.models import get_default_llm, get_chroma_manager
from api_llm.sql import (
    get_database_manager, get_column_map, get_data_stats,
    SQLGenerator, sanitize_dataframe,
)
from api_llm.rag import retrieve_parallel
from api_llm.memory import ConversationMemory  # ← 대화 메모리 추가
from api_llm.utils import (
    StructuredMemory, is_explanation_requested, generate_explanation,
    build_explain_meta,
)
from api_llm.agent import (
    AgentState, entity_linking_node, router_node, sql_generation_node,
    db_execution_node, result_validation_node, visualization_node,
    answer_node, should_retry, should_retry_result, route_by_intent,
)

# 로깅 초기화
setup_logging()
logger = get_logger(__name__)

# ==========================================
# Streamlit 페이지 설정
# ==========================================

st.set_page_config(
    page_title="Enterprise AI Agent",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 엔터프라이즈 재고 분석 시스템")

# ==========================================
# 데이터베이스 연결 상태 표시 (사이드바)
# ==========================================
with st.sidebar:
    st.markdown("### 🔌 시스템 상태")
    
    # 데이터베이스 연결 상태
    if '✅' in db_resources.get('status', ''):
        st.success(db_resources.get('status', '✅ 연결 완료'))
    else:
        st.warning(db_resources.get('status', '⚠️  부분 연결'))
    
    # 상세 정보
    with st.expander("📊 연결 정보"):
        st.write(f"**데이터베이스**: {DATABASE_CONFIG['DB_NAME']}")
        st.write(f"**호스트**: {DATABASE_CONFIG['HOST']}")
        st.write(f"**스키마**: {DATABASE_CONFIG['SCHEMA']}")
        st.write(f"**상태**: {db_resources.get('status', '확인 불가')}")


# ==========================================
# Session State 초기화 (페이지 로드 시 최우선)
# ==========================================

# 데이터베이스 연결 상태 초기화
if "db_status" not in st.session_state:
    st.session_state.db_status = db_resources.get('status', '❌ 연결 실패')
    st.session_state.db_manager = db_resources.get('db_manager')
    st.session_state.chroma_manager = db_resources.get('chroma_manager')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "데이터 분석준비 완료. 질문해주세요."}
    ]

if "structured_memory" not in st.session_state:
    st.session_state.structured_memory = {}

if "work_context" not in st.session_state:
    st.session_state.work_context = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "last_query_context" not in st.session_state:
    st.session_state.last_query_context = None

if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory(
        max_entries=100,
        similarity_threshold=0.85,
        db_url=DATABASE_URL,
        user_id=st.session_state.session_id
    )
    
    # DB에서 최근 대화 로드
    memory = st.session_state.conversation_memory
    if memory.db_manager and memory.db_manager.conn:
        try:
            recent_conversations = memory.load_recent_from_db(limit=20)
            if recent_conversations:
                logger.info(f"📚 DB에서 {len(recent_conversations)}개 최근 대화 로드됨 (사용자: {memory.user_id})")
        except Exception as e:
            logger.warning(f"⚠️ DB 대화 로드 실패: {e}")


# ==========================================
# 리소스 초기화 (캐시)
# ==========================================

@st.cache_resource
def initialize_resources():
    """시작 시 1회만 리소스 로드"""
    logger.info("🔄 리소스 초기화 중...")
    
    try:
        # API 키 검증
        from config import GOOGLE_API_KEY
        if not GOOGLE_API_KEY:
            st.error(
                "❌ Google API 키가 설정되지 않았습니다.\n\n"
                "해결 방법:\n"
                "1. `.env` 파일에 다음을 추가하세요:\n"
                "   ```\n"
                "   GOOGLE_API_KEY=your-api-key\n"
                "   ```\n"
                "2. https://ai.google.dev/aistudio 에서 API 키 생성\n"
                "3. streamlit 재시작"
            )
            st.stop()
        
        # DB 매니저
        db_manager = get_database_manager()
        column_map = db_manager.get_column_map()
        data_stats = db_manager.get_data_stats()
        
        # LLM
        llm = get_default_llm()
        
        # ChromaDB
        chroma_manager = get_chroma_manager()
        collections = chroma_manager.get_all_collections()
        
        # SQL 제너레이터
        schema_ctx = _build_schema_context(column_map)
        sql_gen = SQLGenerator(llm=llm, schema_ctx=schema_ctx, column_map=column_map)
        
        # 엔티티 캐시 (ChromaDB entities 컬렉션에서 로드)
        entity_cache = _load_entity_cache(chroma_manager)
        
        logger.info("✅ 모든 리소스 로드 완료")
        
        return {
            "db_manager": db_manager,
            "column_map": column_map,
            "data_stats": data_stats,
            "llm": llm,
            "chroma_manager": chroma_manager,
            "collections": collections,
            "sql_generator": sql_gen,
            "entity_cache": entity_cache,
        }
    
    except Exception as e:
        logger.exception("리소스 로드 실패")
        st.error(
            f"❌ 시스템 초기화 실패\n\n"
            f"오류: {str(e)[:200]}\n\n"
            "**할당량 초과**인 경우:\n"
            "- Google Gemini Free Tier: 20회/일 제한\n"
            "- 모든 계정의 API 키가 같은 할당량 공유\n\n"
            "**해결 방법:**\n"
            "1. 내일 자정(UTC)에 자동 리셋 대기\n"
            "2. 유료 API 키로 업그레이드: https://console.cloud.google.com/\n"
            "3. 또는 로컬 LLM 모델 사용 검토"
        )
        st.stop()


def _build_schema_context(column_map: Dict) -> str:
    """컬럼 맵으로부터 스키마 컨텍스트 생성"""
    ctx = ""
    for table, cols in column_map.items():
        ctx += f"\n- {table}: {', '.join(cols)}"
    return ctx


def _load_entity_cache(chroma_manager) -> Dict:
    """제조사/고객사 목록 + 벡터 임베딩 로드 (ChromaDB entities 컬렉션에서)"""
    try:
        from sqlalchemy import text
        import numpy as np
        from sentence_transformers import SentenceTransformer
        
        db_manager = get_database_manager()
        engine = db_manager.get_engine()
        schema = DATABASE_CONFIG.get("SCHEMA", "public")
        
        # 1. 기본 엔티티 목록 로드 (DB에서)
        with engine.connect() as conn:
            # manufacturers 테이블 쿼리
            m_query = f"SELECT manufacturer_name FROM {schema}.manufacturers LIMIT 1000"
            m_rows = conn.execute(text(m_query)).fetchall()
            
            # vendors 테이블 쿼리
            v_query = f"SELECT vendor_name FROM {schema}.vendors LIMIT 1000"
            v_rows = conn.execute(text(v_query)).fetchall()
            
            manufacturers = [r[0] for r in m_rows]
            vendors = [r[0] for r in v_rows]
            
            logger.info(f"✅ 엔티티 캐시 로드: 제조사 {len(manufacturers)}개, 고객사 {len(vendors)}개")
        
        # 2. ChromaDB entities 컬렉션에서 임베딩 로드
        try:
            logger.info("🔄 ChromaDB에서 entities 컬렉션 로드 중...")
            entities_collection = chroma_manager.get_collection("entities")
            
            if entities_collection:
                # 문서, 임베딩, 메타데이터 로드
                results = entities_collection.get(
                    include=["documents", "embeddings", "metadatas"]
                )
                
                if results and results["documents"] and len(results["documents"]) > 0:
                    # embeddings를 numpy array로 변환
                    embeddings = np.array(results["embeddings"], dtype=np.float32)
                    
                    # 모델 로드 (entity_linking_node에서 사용)
                    logger.info("⚙️  sentence-transformers 모델 로드 중...")
                    model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
                    
                    embeddings_data = {
                        "model": model,
                        "model_name": "distiluse-base-multilingual-cased-v2",
                        "entities": results["documents"],
                        "manufacturers": manufacturers,
                        "vendors": vendors,
                        "embeddings": embeddings,
                    }
                    
                    logger.info(f"✅ 엔티티 임베딩 로드 완료 | 형태: {embeddings_data['embeddings'].shape}")
                    return {
                        "manufacturers": manufacturers,
                        "vendors": vendors,
                        "embeddings_data": embeddings_data,
                    }
        
        except Exception as e:
            logger.warning(f"⚠️  ChromaDB entities 컬렉션 로드 실패: {e}")
        
        # 3. ChromaDB 로드 실패 시 기본값 반환 (rapidfuzz fallback 사용)
        logger.warning("💡 임베딩 미사용 - rapidfuzz 폴백 모드")
        return {
            "manufacturers": manufacturers,
            "vendors": vendors,
            "embeddings_data": None,
        }
    
    except Exception as e:
        logger.warning(f"엔티티 캐시 로드 실패: {e}")
        return {
            "manufacturers": [],
            "vendors": [],
            "embeddings_data": None,
        }


# 리소스 로드
resources = initialize_resources()


# ==========================================
# 사이드바 UI
# ==========================================

with st.sidebar:
    st.header("🏢 AI 관제실")
    
    # 데이터 통계
    st.info(
        f"📅 데이터 기간: {resources['data_stats'].get('min_date', '')} ~ "
        f"{resources['data_stats'].get('max_date', '')}"
    )
    
    # RAG 상태 (3가지만 사용)
    collections = resources.get("collections", {})
    if collections:
        st.success("✅ RAG 연결됨")
        # 실제 사용되는 3가지만 표시
        used_collections = ["FEWSHOT", "BIZTERM", "SCHEMA"]
        for key in used_collections:
            if key in collections:
                coll = collections[key]
                cnt = coll.count() if coll else 0
                st.caption(f"{key}: {cnt}건")
    
    # ─── 대화 메모리 통계 ───────────────────────────────────
    st.divider()
    st.subheader("💭 대화 메모리 & DB")
    
    # 메모리 통계 표시
    stats = st.session_state.conversation_memory.get_stats()
    memory_stats = stats.get("memory", {})
    db_stats = stats.get("database", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("메모리 대화", memory_stats.get("total_conversations", 0))
    with col2:
        st.metric("Hot 데이터 (1개월)", db_stats.get("active_conversations", 0))
    with col3:
        st.metric("학습용 데이터", db_stats.get("training_data_records", 0))
    
    st.metric(
        "메모리 사용",
        f"{memory_stats.get('memory_usage_mb', 0)} MB",
        "임베딩 캐시 포함"
    )
    
    # 대화 히스토리 표시
    if memory_stats.get("total_conversations", 0) > 0:
        if st.checkbox("📝 대화 히스토리 보기"):
            st.caption("**최근 대화 5개 (DB):**")
            from api_llm.utils.training_logger import get_recent_conversations
            
            history = get_recent_conversations(limit=5)
            for i, conv in enumerate(history, 1):
                with st.expander(f"{i}. {conv['question'][:60]}..."):
                    st.text(f"⏰ {conv['timestamp']}")
                    st.text(f"📄 응답: {conv.get('response_summary', '')[:100]}...")
    
    # DB 관리 기능
    if st.session_state.conversation_memory.db_manager:
        st.caption("**🗄️ DB 관리:**")
        db_col1, db_col2 = st.columns(2)
        
        with db_col1:
            if st.button("📦 아카이빙 실행 (1개월→Archive)"):
                result = st.session_state.conversation_memory.archive_expired_conversations()
                st.info(f"✅ {result.get('message', '완료')}")
        
        with db_col2:
            if st.button("📊 학습 데이터 내보내기"):
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir='.') as f:
                    if st.session_state.conversation_memory.export_training_data(f.name):
                        st.success(f"✅ 내보냈습니다: {f.name}")
                        # 파일 다운로드 제공
                        with open(f.name, "r") as file:
                            st.download_button("📥 다운로드", file.read(), "training_data.json")
    
    # 메모리 내보내기
    if memory_stats.get("total_conversations", 0) > 0:
        if st.button("📥 세션 메모리 내보내기 (JSON)"):
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                st.session_state.conversation_memory.export_to_json(f.name)
                st.success(f"✅ 내보냈습니다: {f.name}")
    
    # 메모리 초기화 (확인 필수)
    if st.button("🗑️ 세션 메모리 초기화"):
        st.session_state.conversation_memory.clear()
        st.success("메모리 초기화 완료")
        st.rerun()



# ==========================================
# LangGraph 워크플로우 연결
# ==========================================

@st.cache_resource
def build_workflow():
    """LangGraph 워크플로우 구축"""
    
    workflow = StateGraph(AgentState)
    
    # 노드 등록
    workflow.add_node("refine", lambda s: entity_linking_node(s, resources["entity_cache"]))
    workflow.add_node("router", lambda s: router_node(s, llm=resources["llm"]))
    workflow.add_node("sql_gen", lambda s: sql_generation_node(
        s,
        llm=resources["llm"],
        sql_generator=resources["sql_generator"],
        column_map=resources["column_map"],
        data_stats=resources["data_stats"],
        entity_cache=resources["entity_cache"],
    ))
    workflow.add_node("db_exec", lambda s: db_execution_node(
        s,
        column_map=resources["column_map"],
    ))
    workflow.add_node("result_validate", result_validation_node)
    workflow.add_node("visual", visualization_node)
    workflow.add_node("answer", lambda s: answer_node(s, llm=resources["llm"]))
    
    # 엣지 설정
    workflow.set_entry_point("refine")
    workflow.add_edge("refine", "router")
    
    workflow.add_conditional_edges(
        "router",
        route_by_intent,
        {"answer": "answer", "sql_gen": "sql_gen"}
    )
    
    workflow.add_edge("sql_gen", "db_exec")
    
    workflow.add_conditional_edges(
        "db_exec",
        should_retry,
        {"retry": "sql_gen", "success": "result_validate"}
    )
    
    workflow.add_conditional_edges(
        "result_validate",
        should_retry_result,
        {"retry": "sql_gen", "visual": "visual"}
    )
    
    workflow.add_edge("visual", "answer")
    workflow.add_edge("answer", END)
    
    return workflow.compile()


app_agent = build_workflow()


# ==========================================
# 메시지 렌더링
# ==========================================

def _format_xaxis_data(df: pd.DataFrame, x_col: str) -> pd.DataFrame:
    """
    X축 데이터 자동 포맷팅 (년도+분기+월 자동 결합)
    - 날짜 컬럼: 년도 Q분기 형식으로 변환
    - 별도의 년/분기 컬럼: 자동으로 결합
    """
    if x_col not in df.columns:
        return df
    
    df = df.copy()
    
    # 1️⃣ datetime 컬럼인 경우
    if pd.api.types.is_datetime64_any_dtype(df[x_col]):
        df['year'] = df[x_col].dt.year
        df['quarter'] = 'Q' + (df[x_col].dt.quarter).astype(str)
        df[x_col] = df['year'].astype(str) + '년 ' + df['quarter']
        df = df.drop(['year', 'quarter'], axis=1)
    
    # 2️⃣ 년도 + 분기 컬럼이 별도로 있는 경우
    elif 'year' in df.columns and any(q_col in df.columns for q_col in ['quarter', 'q', 'quater']):
        q_col = next((col for col in ['quarter', 'q', 'quater'] if col in df.columns), None)
        if q_col:
            df[x_col] = df['year'].astype(str) + '년 ' + df[q_col].astype(str)
    
    return df


def render_response(
    content: str,
    sql: Optional[str] = None,
    df: Optional[pd.DataFrame] = None,
    chart_info: Optional[Dict] = None,
    show_satisfaction: bool = False,
    question: Optional[str] = None,
    schema_snapshot: Optional[str] = None,
):
    """응답 렌더링 + 차트 표시 + 사용자 만족도 평가"""
    st.write(content)
    
    if sql:
        with st.expander("🔍 실행된 SQL 보기"):
            st.code(sql, language="sql")
    
    if df is not None and not df.empty:
        st.subheader("📋 데이터 테이블")
        st.dataframe(df, use_container_width=True)
    
    # 차트 표시 (Recharts 호환 JSON 구조 기반, Plotly로 렌더링)
    if chart_info and chart_info.get("type") not in ("none", None, "table"):
        try:
            import plotly.graph_objects as go

            chart_type   = chart_info.get("type", "bar")
            title        = chart_info.get("title", "Data Visualization")
            x_col        = chart_info.get("xKey")
            data_keys    = chart_info.get("dataKeys", [])   # List[str]
            use_dual     = chart_info.get("useSecondaryAxis", False)
            y_axes       = chart_info.get("yAxes", {})      # {"col": "primary"|"secondary"}
            raw_data     = chart_info.get("data")           # Recharts data[] (list of dicts)

            # ── DataFrame 재구성: chart_info["data"] 우선, 없으면 원본 df 사용 ──
            if raw_data:
                plot_df = pd.DataFrame(raw_data)
            elif df is not None and not df.empty:
                plot_df = df.copy()
            else:
                plot_df = None

            if plot_df is None or plot_df.empty or not x_col or not data_keys:
                st.warning(f"📊 차트 데이터 없음: xKey={x_col!r}, dataKeys={data_keys}, 데이터 행={len(plot_df) if plot_df is not None else 0}")
            else:
                # X축 데이터 자동 포맷팅 (년도+분기 등 자동 결합)
                plot_df = _format_xaxis_data(plot_df, x_col)
                y_cols = [c for c in data_keys if c in plot_df.columns]

                if not y_cols:
                    st.warning(f"📊 차트 y축 컬럼 없음: dataKeys={data_keys} → 실제 컬럼: {list(plot_df.columns)}")
                else:
                    st.subheader(f"📊 {title}")
                    fig = go.Figure()

                    # ── Dual Y-Axis (Bar / Line) ─────────────────────────
                    if use_dual and len(y_cols) > 1:
                        primary_cols   = [c for c in y_cols if y_axes.get(c) != "secondary"]
                        secondary_cols = [c for c in y_cols if y_axes.get(c) == "secondary"]

                        for col in primary_cols:
                            trace = (go.Scatter(x=plot_df[x_col], y=plot_df[col],
                                                mode="lines+markers", name=col, yaxis="y")
                                     if chart_type == "line"
                                     else go.Bar(x=plot_df[x_col], y=plot_df[col],
                                                 name=col, yaxis="y"))
                            fig.add_trace(trace)

                        for col in secondary_cols:
                            trace = (go.Scatter(x=plot_df[x_col], y=plot_df[col],
                                                mode="lines+markers", name=col, yaxis="y2")
                                     if chart_type == "line"
                                     else go.Bar(x=plot_df[x_col], y=plot_df[col],
                                                 name=col, yaxis="y2", opacity=0.7))
                            fig.add_trace(trace)

                        fig.update_layout(
                            title=dict(text=title, font=dict(size=18, color="#1f77b4"), x=0.5, xanchor="center"),
                            xaxis=dict(title=x_col, type="category", tickangle=-45, tickfont=dict(size=12)),
                            yaxis=dict(
                                title=dict(text=primary_cols[0] if primary_cols else "Primary",
                                           font=dict(color="blue", size=13)),
                                tickfont=dict(color="blue", size=11),
                            ),
                            yaxis2=dict(
                                title=dict(text=secondary_cols[0] if secondary_cols else "Secondary",
                                           font=dict(color="red", size=13)),
                                tickfont=dict(color="red", size=11),
                                overlaying="y", side="right",
                            ),
                            hovermode="x unified", height=550,
                            margin=dict(t=80, b=100, l=80, r=80),
                            showlegend=True, font=dict(size=12),
                        )

                    # ── 단일 축 Bar ──────────────────────────────────────
                    elif chart_type == "bar":
                        for col in y_cols:
                            fig.add_trace(go.Bar(x=plot_df[x_col], y=plot_df[col], name=col))
                        fig.update_layout(
                            title=dict(text=title, font=dict(size=18, color="#1f77b4"), x=0.5, xanchor="center"),
                            xaxis=dict(title=x_col, type="category", tickangle=-45, tickfont=dict(size=12)),
                            yaxis=dict(title=y_cols[0], tickfont=dict(size=11)),
                            barmode="group", height=550,
                            margin=dict(t=80, b=100, l=80, r=50),
                            showlegend=True, font=dict(size=12),
                        )

                    # ── 단일 축 Line ─────────────────────────────────────
                    elif chart_type == "line":
                        for col in y_cols:
                            fig.add_trace(go.Scatter(x=plot_df[x_col], y=plot_df[col],
                                                     mode="lines+markers", name=col))
                        fig.update_layout(
                            title=dict(text=title, font=dict(size=18, color="#1f77b4"), x=0.5, xanchor="center"),
                            xaxis=dict(title=x_col, type="category", tickangle=-45, tickfont=dict(size=12)),
                            yaxis=dict(title="값", tickfont=dict(size=11)),
                            hovermode="x unified", height=550,
                            margin=dict(t=80, b=100, l=80, r=50),
                            showlegend=True, font=dict(size=12),
                        )

                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.warning(f"차트 렌더링 오류: {e}")
            st.warning(f"차트 렌더링 중 오류: {str(e)[:100]}")
    
    # 사용자 만족도 평가 (SQL 쿼리 실행 결과인 경우만)
    if show_satisfaction and sql and question:
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            if st.button("👍 좋아요", key=f"like_{abs(hash(sql)) % 100000}"):
                # 만족도: 1 (좋아요)
                from api_llm.utils.training_logger import log_training_data
                result_summary = f"{len(df)} rows" if df is not None and not df.empty else "No data"
                log_training_data(
                    question=question,
                    generated_sql=sql,
                    schema_snapshot=schema_snapshot or "",
                    execution_success=True,
                    execution_result_summary=result_summary,
                    user_satisfaction=1,
                )
                st.success("✅ 피드백이 저장되었습니다")
        
        with col2:
            if st.button("👎 싫어요", key=f"dislike_{abs(hash(sql)) % 100000}"):
                # 만족도: -1 (싫어요)
                from api_llm.utils.training_logger import log_training_data
                result_summary = f"{len(df)} rows" if df is not None and not df.empty else "No data"
                log_training_data(
                    question=question,
                    generated_sql=sql,
                    schema_snapshot=schema_snapshot or "",
                    execution_success=True,
                    execution_result_summary=result_summary,
                    user_satisfaction=-1,
                )
                st.error("❌ 피드백을 수집했습니다. 개선하겠습니다")


# ==========================================
# 메인 채팅 인터페이스
# ==========================================

# 이전 메시지 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_response(
            msg.get("content", ""),
            sql=msg.get("sql_query"),
            df=msg.get("df"),
            chart_info=msg.get("chart_info"),
        )

# 사용자 입력
user_input = st.chat_input("질문하세요...")

if user_input:
    # 사용자 메시지 표시
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # ─── 메모리에서 유사 질문 검색 ───────────────────────────
    memory = st.session_state.conversation_memory
    cached_result = memory.find_similar_question(user_input, embedder=None)
    
    if cached_result:
        # 캐시 히트: 저장된 응답 바로 반환
        logger.info(f"⚡ 캐시 히트 | 즉시 응답")
        st.chat_message("assistant").info(
            "💡 **같은 질문의 이전 결과를 사용합니다** (실시간 처리)\n\n"
            f"원래 질문: *{cached_result['question'][:80]}*"
        )
        
        # 캐시된 응답 렌더링
        cached_response = cached_result["response"]
        with st.chat_message("assistant"):
            render_response(
                cached_response.get("answer", ""),
                sql=cached_response.get("sql_query"),
                df=cached_response.get("df"),
                chart_info=cached_response.get("chart_info"),
            )
        
        # 메시지 히스토리에 추가
        st.session_state.messages.append({
            "role": "assistant",
            "content": cached_response.get("answer", ""),
            "source": "cache",
            "sql_query": cached_response.get("sql_query"),
            "df": cached_response.get("df"),
            "chart_info": cached_response.get("chart_info"),
        })
        
        st.stop()
    
    # 여러 질문 감지 및 분리 (LLM 기반 독립성 판단)
    from agent.nodes import split_multiple_questions
    llm = get_default_llm()
    sub_questions = split_multiple_questions(user_input, llm=llm)
    
    if len(sub_questions) > 1:
        st.info(f"📋 {len(sub_questions)}개의 독립적 질문을 감지했습니다. 각각 처리합니다...")
    
    # 결과 누적 리스트
    all_results = []
    
    # 각 질문 처리
    for idx, sub_q in enumerate(sub_questions, 1):
        st.subheader(f"질문 {idx}: {sub_q}")
        
        # 에이전트 실행
        with st.spinner(f"🤖 사고 및 데이터 처리 중... ({idx}/{len(sub_questions)})"):
            try:
                # ============================================
                # 최근 대화 맥락 추가 (DB에서 조회)
                # ============================================
                from api_llm.utils.training_logger import get_recent_conversations
                
                recent_context = get_recent_conversations(limit=5)
                context_formatted = [
                    {
                        "question": conv.get("question", ""),
                        "timestamp": conv.get("timestamp", ""),
                    }
                    for conv in recent_context
                ]
                
                res = app_agent.invoke({
                    "question": sub_q,
                    "context": context_formatted,  # ← DB에서 가져온 최근 5개 대화
                    "error_history": [],  # ← 각 질문마다 에러 로그 초기화
                    "retry_count": 0,     # ← 각 질문마다 재시도 횟수 초기화
                })
                
                # 데이터 정제
                if res.get("df") is not None:
                    res["df"] = sanitize_dataframe(res["df"])
            
            except Exception as e:
                logger.exception("에이전트 실행 실패")
                st.error(f"❌ 처리 중 오류: {str(e)}")
                continue
        
        # 결과 표시
        df = res.get("df")
        sql_query = res.get("sql_query")
        chart_info = res.get("chart_info")
        raw_ans = res.get("db_result", "응답 실패")
        
        ans = raw_ans  # nodes.py의 answer_node()에서 이미 생성된 응답 사용
        
        # SQL 쿼리가 있으면 만족도 평가 표시 (잡담 제외)
        show_satisfaction = bool(sql_query and "재고" not in raw_ans[:50])
        
        # 스키마 스냅샷 (로깅용)
        schema_snapshot = str(resources.get("column_map", {}))[:500]
        
        with st.chat_message("assistant"):
            render_response(
                ans,
                sql=sql_query,
                df=df,
                chart_info=chart_info,
                show_satisfaction=show_satisfaction,
                question=sub_q,
                schema_snapshot=schema_snapshot,
            )
        
        # 세션 메모리 업데이트
        st.session_state.messages.append({
            "role": "assistant",
            "content": ans,
            "sql_query": sql_query,
            "df": df,
            "chart_info": chart_info,
        })
        
        # ─── 대화 메모리에 저장 (캐시용) ───────────────────────
        memory.add_conversation(
            question=sub_q,
            response={
                "answer": ans,
                "sql_query": sql_query,
                "df": df,
                "chart_info": chart_info,
            },
            metadata={
                "intent": res.get("intent"),
                "sql_query": sql_query,  # ✅ DB 저장용
                "refined_question": res.get("refined_question", sub_q),
                "entity_corrections": res.get("entity_corrections", {}),
                "validation_result": res.get("validation_result", "OK"),
                "execution_success": sql_query is not None,
                "row_count": len(df) if df is not None and hasattr(df, '__len__') else 0,
            },
            save_to_db=True,  # ✅ DB에 저장
        )
        
        all_results.append({
            "question": sub_q,
            "answer": ans,
            "sql": sql_query,
            "df": df,
        })
        
        # 구조화 메모리 업데이트
        if res.get("intent") != "CHIT_CHAT":
            mem = StructuredMemory()
            mem.memory = st.session_state.structured_memory
            mem.update(sub_q, df, res.get("query_plan", {}), sql_query or "")
            st.session_state.structured_memory = mem.get_dict()
        
        st.divider()
    
    # 결과 요약 (여러 질문인 경우)
    if len(sub_questions) > 1:
        st.subheader("📊 결과 요약")
        for result in all_results:
            if result["answer"] and result["answer"] != "응답 실패":
                st.write(f"**{result['question']}**")
                st.write(result["answer"])
                st.divider()


# 푸터
st.markdown("---")
st.caption(f"세션: `{st.session_state.session_id[:8]}...` | 모델: `Gemini 2.5 Flash`")
