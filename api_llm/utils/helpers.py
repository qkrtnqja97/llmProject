# -*- coding: utf-8 -*-
"""
유틸리티 함수 모듈
- 차트 추론
- 결과 설명
- 구조화 메모리 관리
- 엔티티 링킹
"""

import re
import logging
from typing import Dict, List, Tuple, Optional

import pandas as pd
from rapidfuzz import process, fuzz

from api_llm.config import CHART_KEYWORDS, EXPLAIN_TRIGGERS

logger = logging.getLogger(__name__)


# ==========================================
# 시각화 관련 함수
# ==========================================

def infer_chart_type(question: str) -> str:
    """질문 키워드 기반 차트 타입 추론"""
    q = question.lower()
    
    if any(k in q for k in ["파이", "비율", "점유", "pie"]):
        return "pie"
    if any(k in q for k in ["추이", "변화", "흐름", "트렌드", "선", "line", "시계열", "월별", "일별"]):
        return "line"
    
    # 막대 그래프 우선 (판매, 수량 등은 막대 그래프가 더 어울림)
    if any(k in q for k in ["판매", "수량", "개수", "매출", "비교", "순위", "top"]):
        return "bar"
    
    return "bar"  # 기본값


def infer_chart_columns(df: pd.DataFrame) -> Tuple[str, str]:
    """DataFrame 컬럼 타입 기반 x/y축 자동 추론"""
    cols = df.columns.tolist()
    
    # 숫자형 컬럼 탐지
    num_cols = df.select_dtypes(include="number").columns.tolist()
    str_cols = [c for c in cols if c not in num_cols]
    
    x = str_cols[0] if str_cols else cols[0]
    y = num_cols[0] if num_cols else (cols[1] if len(cols) > 1 else cols[0])
    
    return x, y


def sanitize_chart_info(chart_info: Dict, df_columns: List) -> Dict:
    """LLM 출력 chart_info를 안전하게 정규화"""
    x = chart_info.get("x", "")
    y = chart_info.get("y", "")
    
    # 리스트로 반환된 경우 첫 번째 원소만 사용
    if isinstance(x, list):
        x = x[0] if x else ""
    if isinstance(y, list):
        y = y[0] if y else ""
    
    x = str(x).strip()
    y = str(y).strip()
    
    # 실제 컬럼명 검증
    if x not in df_columns or y not in df_columns:
        num_cols = [c for c in df_columns if c not in (x,)]
        x = df_columns[0] if df_columns else x
        y = num_cols[0] if num_cols else (df_columns[1] if len(df_columns) > 1 else y)
        logger.warning(f"차트 컬럼 자동 보정: x={x}, y={y}")
    
    return {"type": chart_info.get("type", "none"), "x": x, "y": y}


def is_chart_requested(question: str) -> bool:
    """질문에서 차트 요청 여부 판단"""
    return any(kw in question for kw in CHART_KEYWORDS)


# ==========================================
# 결과 설명 (Explainability)
# ==========================================

def build_explain_meta(sql: str, df: Optional[pd.DataFrame], plan: Dict) -> Dict:
    """실행 결과에서 설명 메타데이터 추출"""
    
    # 사용 테이블
    tables_used = list(set(re.findall(
        r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)', sql, re.IGNORECASE
    )))
    
    # 집계 함수
    agg_matches = re.findall(
        r'(SUM|AVG|COUNT|MAX|MIN)\s*\(([^)]+)\)', sql, re.IGNORECASE
    )
    aggregations = [f"{fn}({col.strip()})" for fn, col in agg_matches]
    
    # WHERE 조건
    filters_applied = []
    where_m = re.search(
        r'WHERE\s+(.*?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)',
        sql, re.IGNORECASE | re.DOTALL
    )
    if where_m:
        raw_where = where_m.group(1).strip()
        filters_applied = [f.strip() for f in
                          re.split(r'\bAND\b|\bOR\b', raw_where, flags=re.IGNORECASE)
                          if f.strip()]
    
    return {
        "sql_used": sql,
        "tables_used": tables_used,
        "aggregations": aggregations,
        "filters_applied": filters_applied[:5],
        "group_by": (plan or {}).get("group_by", "none"),
        "row_count": len(df) if df is not None else 0,
        "intent_summary": (plan or {}).get("intent_summary", ""),
    }


def generate_explanation(meta: Dict, question: str) -> str:
    """설명 메타데이터로부터 사용자 친화적 설명 생성"""
    lines = [f"**'{question}'** 계산 방법:"]
    
    if meta.get("tables_used"):
        lines.append(f"- 사용 테이블: `{'`, `'.join(meta['tables_used'])}`")
    
    if meta.get("aggregations"):
        lines.append(f"- 집계 방식: {', '.join(meta['aggregations'])}")
    
    if meta.get("filters_applied"):
        lines.append(f"- 적용 필터: {' AND '.join(meta['filters_applied'][:3])}")
    
    if meta.get("group_by") and meta["group_by"] != "none":
        lines.append(f"- 그룹 기준: {meta['group_by']}")
    
    lines.append(f"- 결과 행수: {meta.get('row_count', 0)}건")
    
    if meta.get("sql_used"):
        lines.append(f"\n```sql\n{meta['sql_used']}\n```")
    
    return "\n".join(lines)


def is_explanation_requested(question: str) -> bool:
    """설명 요청 여부 판단"""
    return any(trigger in question for trigger in EXPLAIN_TRIGGERS)


# ==========================================
# 구조화 메모리 (Structured Memory)
# ==========================================

class StructuredMemory:
    """대명사/생략 표현 해석을 위한 팀무토리 관리"""

    def __init__(self):
        self.memory: Dict[str, any] = {}

    def update(self, question: str, df: Optional[pd.DataFrame],
               plan: Dict, sql: str) -> None:
        """
        쿼리 결과에서 구조화 메모리 업데이트
        
        last_product, last_vendor, last_manufacturer, last_date_range 등
        """
        q_lower = question.lower()

        # 메트릭 종류 판단
        if any(k in q_lower for k in ["매출", "revenue", "판매금"]):
            self.memory["last_metric"] = "매출액"
        elif any(k in q_lower for k in ["매입", "purchase", "구매"]):
            self.memory["last_metric"] = "매입액"
        elif any(k in q_lower for k in ["수익", "이익", "profit"]):
            self.memory["last_metric"] = "수익"
        elif any(k in q_lower for k in ["재고", "stock", "수량"]):
            self.memory["last_metric"] = "재고수량"

        # 최근 제품
        if df is not None and "part_number" in df.columns and len(df) > 0:
            self.memory["last_product"] = str(df.iloc[0]["part_number"])

        # 날짜 범위
        filters = plan.get("filters", {}) if plan else {}
        date_range = {}
        if filters.get("year"):
            date_range["year"] = filters["year"]
        if filters.get("quarter"):
            date_range["quarter"] = filters["quarter"]
        if date_range:
            self.memory["last_date_range"] = date_range

        # 고객사/제조사
        if df is not None:
            if "vendor_name" in df.columns and len(df) > 0:
                self.memory["last_vendor"] = str(df.iloc[0]["vendor_name"])
            if "name" in df.columns and len(df) > 0:
                self.memory["last_manufacturer"] = str(df.iloc[0]["name"])

        if filters.get("category"):
            self.memory["last_category"] = filters["category"]

        self.memory["last_sql"] = sql
        self.memory["last_filters"] = filters

    def inject_to_question(self, question: str) -> str:
        """구조화 메모리로 대명사/생략 표현 자동 보완"""
        if not self.memory:
            return question
        
        q = question
        PRONOUN_MAP = {
            "이 제품": "last_product", "해당 제품": "last_product", "그 제품": "last_product",
            "이 고객사": "last_vendor", "해당 고객사": "last_vendor",
            "이 제조사": "last_manufacturer", "해당 제조사": "last_manufacturer",
        }
        
        for pronoun, key in PRONOUN_MAP.items():
            if pronoun in q and self.memory.get(key):
                q = q.replace(pronoun, f"'{self.memory[key]}'")
        
        if "같은 기간" in q and self.memory.get("last_date_range"):
            q += f" (기간: {self.memory['last_date_range']})"
        
        return q

    def get_dict(self) -> Dict:
        """메모리 딕셔너리 반환"""
        return self.memory.copy()

    def clear(self) -> None:
        """메모리 초기화"""
        self.memory.clear()


# ==========================================
# 엔티티 링킹 (오타 보정)
# ==========================================

def correct_entity_typos(
    question: str,
    manufacturers: List[str],
    vendors: List[str],
    embeddings_data: Dict = None,
) -> Tuple[str, str]:
    """
    벡터 기반 회사명/제품명 오타 보정 (빠름!)
    
    Args:
        embeddings_data: {
            "manufacturers_vec": np.array,
            "vendors_vec": np.array,
            "embedding_model": SentenceTransformer,
        }
    
    Returns:
        (수정된 질문, 동의어 힌트)
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    
    refined = question
    hint = ""
    
    names = manufacturers + vendors
    if not names:
        return question, hint
    
    # ✅ 벡터 기반 처리 (사용 가능한 경우)
    if (embeddings_data and embeddings_data.get("embedding_model") is not None 
        and embeddings_data.get("manufacturers_vec") is not None):
        
        try:
            model = embeddings_data["embedding_model"]
            m_vecs = embeddings_data["manufacturers_vec"]
            v_vecs = embeddings_data["vendors_vec"]
            all_vecs = np.vstack([m_vecs, v_vecs]) if len(v_vecs) > 0 else m_vecs
            
            # 3자 이상 단어만 검사
            words = [w for w in question.split() if len(w) >= 3]
            
            if words and len(all_vecs) > 0:
                # 단어 벡터화
                word_vecs = model.encode(words, convert_to_numpy=True)
                
                # 코사인 유사도 계산
                similarities = cosine_similarity(word_vecs, all_vecs)
                
                for i, word in enumerate(words):
                    best_idx = similarities[i].argmax()
                    best_score = similarities[i][best_idx]
                    
                    # 임계값: 0.85
                    if best_score > 0.85:
                        best_name = names[best_idx]
                        if word != best_name:
                            refined = refined.replace(word, best_name, 1)
                            hint += f"'{word}' → '{best_name}' ({best_score:.2f}) | "
                
                if hint:
                    hint = hint.rstrip(" | ")
                    logger.info(f"🎯 벡터 기반 오타 보정: {hint}")
                
                return refined, hint
        
        except Exception as e:
            logger.warning(f"⚠️ 벡터 기반 처리 실패: {e}, rapidfuzz로 폴백")
    
    # ❌ 폴백: rapidfuzz 사용 (벡터 사용 불가 시)
    for word in question.split():
        if len(word) >= 2:
            match = process.extractOne(word, names, scorer=fuzz.ratio)
            if match and match[1] > 70:
                refined = refined.replace(word, match[0])
                hint += f"'{word}' → '{match[0]}' | "
    
    if hint:
        hint = hint.rstrip(" | ")
        logger.info(f"엔티티 오타 보정 (rapidfuzz): {hint}")
    
    return refined, hint
