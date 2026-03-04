# -*- coding: utf-8 -*-
"""
SQL 검증 모듈
- SQL 구문 검증 (sqlglot 사용)
- 컬럼 소속 검증 (AST 기반, 따옴표 포함)
- GROUP BY 검증
- JOIN 규칙 검증

이제 내부에서 sqlglot 파서를 이용해 테이블/별칭/컬럼을 추출하고,
여전히 파싱 실패 시 정규식 폴백을 수행합니다.
"""

import re
import logging
from typing import Tuple

import sqlglot
from sqlglot.errors import ParseError

from api_llm.config import VALID_JOINS

logger = logging.getLogger(__name__)


def validate_sql_syntax(sql: str) -> Tuple[bool, str]:
    """
    SQL 구문 검증 (sqlglot 파싱)
    
    Returns:
        (is_valid, error_message)
    """
    # sqlglot 파싱 검증
    try:
        sqlglot.parse_one(sql, dialect="postgres")
    except ParseError as e:
        logger.warning(f"SQL 파싱 경고: {str(e)[:200]}")
        return False, f"SQL 문법 오류: {str(e)[:200]}"
    except Exception as e:
        logger.warning(f"SQL 예외: {str(e)[:200]}")
        return False, f"SQL 오류: {str(e)[:200]}"
    
    return True, ""


def _extract_alias_map(sql: str) -> dict:
    """SQL 문자열에서 테이블별칭 → 실제 테이블명을 추출한다.

    가능한 경우 **sqlglot** 파서를 사용하여 AST에서 정보를 가져오며,
    실패 시 기존의 정규식을 이용한 폴백을 수행한다.

    반환값은 alias_map으로, alias_map[alias] = table, alias_map[table] = table 형태
    로 정상화해서 다른 검사 함수들이 편하게 사용할 수 있도록 한다.
    """
    alias_map = {}
    try:
        tree = sqlglot.parse_one(sql, dialect="postgres")
        for table in tree.find_all(sqlglot.exp.Table):
            tbl_name = table.name.lower()
            alias = table.alias_or_name.lower()
            alias_map[alias] = tbl_name
            alias_map[tbl_name] = tbl_name
    except Exception:
        # 파싱에 실패하면 기존 정규식을 사용한다.
        table_pattern = re.compile(
            r'(?:FROM|JOIN)\s+(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)(?:\.)?(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)',
            re.IGNORECASE,
        )
        for m in table_pattern.finditer(sql):
            # 그룹핑을 조금 복잡하게 했기 때문에 단순화
            parts = re.findall(r'"([^"]+)"|([a-zA-Z_][a-zA-Z0-9_]*)', m.group(0))
            # 마지막 두 결과가 [table, alias]
            if len(parts) >= 2:
                tbl = parts[-2][0] or parts[-2][1]
                alias = parts[-1][0] or parts[-1][1]
                tbl, alias = tbl.lower(), alias.lower()
                alias_map[alias] = tbl
                alias_map[tbl] = tbl
    return alias_map


def validate_column_ownership(sql: str, column_map: dict) -> Tuple[bool, str]:
    """
    SQL의 테이블별칭.컬럼 패턴을 추출해서 DB COLUMN_MAP과 대조

    Returns:
        (is_valid, error_message)
    """
    if not column_map:
        return True, ""

    alias_map = _extract_alias_map(sql)
    if not alias_map:
        return True, ""

    # column_map 키 정규화 (스키마 포함된 이름을 테이블명만으로 변환)
    column_map_normalized = {}
    for key, cols in column_map.items():
        table_name = key.split('.')[-1] if '.' in key else key
        column_map_normalized[table_name.lower()] = cols

    errors = []

    # AST 기반으로 컬럼 참조를 순회하여 검사
    try:
        tree = sqlglot.parse_one(sql, dialect="postgres")
        for col in tree.find_all(sqlglot.exp.Column):
            table = col.table
            column = col.name
            if not table or not column:
                continue
            alias = table.lower()
            if alias not in alias_map:
                continue
            actual_table = alias_map[alias]
            if actual_table not in column_map_normalized:
                continue
            valid_cols = [c.lower() for c in column_map_normalized[actual_table]]
            if column.lower() not in valid_cols:
                found_in = [t for t, cols in column_map_normalized.items()
                           if column.lower() in [c.lower() for c in cols]]
                hint = f"'{column}' 컬럼이 '{actual_table}' 테이블에 없음"
                if found_in:
                    hint += f" → '{found_in[0]}' 테이블에 존재. JOIN 필요."
                errors.append(hint)
    except Exception:
        # 파싱 실패 시 간단한 정규식 폴백 (구 버전과 동일)
        col_ref_pattern = re.compile(
            r'\b(?:(?:"([^"]+)")|([a-zA-Z_][a-zA-Z0-9_]*))\.(?:(?:"([^"]+)")|(\w+))\b'
        )
        for m in col_ref_pattern.finditer(sql):
            alias = (m.group(1) or m.group(2)).lower()
            col = (m.group(3) or m.group(4)).lower()
            if alias not in alias_map:
                continue
            actual_table = alias_map[alias]
            if actual_table not in column_map_normalized:
                continue
            valid_cols = [c.lower() for c in column_map_normalized[actual_table]]
            if col not in valid_cols:
                found_in = [t for t, cols in column_map_normalized.items()
                           if col in [c.lower() for c in cols]]
                hint = f"'{col}' 컬럼이 '{actual_table}' 테이블에 없음"
                if found_in:
                    hint += f" → '{found_in[0]}' 테이블에 존재. JOIN 필요."
                errors.append(hint)

    if errors:
        return False, " | ".join(errors)

    return True, ""

def validate_sql_static(sql: str, column_map: dict) -> Tuple[bool, str, str]:
    """
    Python 레벨 SQL 구조 검증
    
    Returns:
        (is_valid, error_message, retry_strategy)
    """
    # 스키마.테이블 형식을 테이블만으로 정규화 (schema.table → table)
    sql_normalized = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\.(?=[a-zA-Z_])', '', sql)
    
    # alias map은 AST 또는 정규식으로 추출
    alias_map = _extract_alias_map(sql)

    sql_upper = sql_normalized.upper()
    errors = []
    strategy = "syntax"
    
    # 1. SELECT * 금지
    if re.search(r'SELECT\s+\*', sql_upper):
        errors.append("SELECT * 금지. 필요한 컬럼을 명시하세요.")
        strategy = "syntax"
    
    # 2. GROUP BY 누락 검사
    has_agg = bool(re.search(r'\b(SUM|AVG|COUNT|MAX|MIN)\s*\(', sql_upper))
    has_grp = bool(re.search(r'\bGROUP\s+BY\b', sql_upper))
    has_win = bool(re.search(r'\bOVER\s*\(', sql_upper))
    
    if has_agg and not has_grp and not has_win:
        # CTE가 있는 경우 마지막 SELECT를 기준으로 검사 (CTE 내부 집계와 혼동 방지)
        all_sel_contents = re.findall(r'SELECT\s+(.*?)\s+FROM', sql_normalized, re.IGNORECASE | re.DOTALL)
        sel_content = all_sel_contents[-1] if all_sel_contents else None
        if sel_content:
            cleaned = re.sub(r'(SUM|AVG|COUNT|MAX|MIN)\s*\([^)]+\)', '', sel_content, flags=re.IGNORECASE)
            non_agg = [c.strip() for c in cleaned.split(',')
                      if c.strip() and c.strip() not in ('', '*')]
            # 마지막 SELECT 자체에 집계함수가 있을 때만 경고
            has_agg_in_final = bool(re.search(r'\b(SUM|AVG|COUNT|MAX|MIN)\s*\(', sel_content, re.IGNORECASE))
            if non_agg and has_agg_in_final:
                errors.append("GROUP BY 누락: 비집계 컬럼이 있습니다. GROUP BY를 추가하세요.")
                strategy = "logic"
    
    # 3. Cartesian Product 감지 (CROSS JOIN은 ON 불필요이므로 카운트 제외)
    cross_join_cnt = len(re.findall(r'\bCROSS\s+JOIN\b', sql_upper))
    join_cnt = len(re.findall(r'\bJOIN\b', sql_upper)) - cross_join_cnt
    on_cnt = len(re.findall(r'\bON\b|\bUSING\b', sql_upper))
    if join_cnt > 0 and on_cnt < join_cnt:
        errors.append(f"Cartesian Product 위험: JOIN {join_cnt}개, ON {on_cnt}개")
        strategy = "logic"

    # 4. 존재하지 않는 테이블 참조 (schema.table 형식 지원)
    sql_clean = re.sub(r'EXTRACT\s*\([^)]+\)', 'EXTRACT_PLACEHOLDER', sql_normalized, flags=re.IGNORECASE)
    # FROM/JOIN 뒤에 오는 함수 호출 패턴도 치환 (GENERATE_SERIES, UNNEST 등)
    # lookbehind 대신 캡처 그룹 사용 → 다중 공백·개행 모두 처리
    sql_clean = re.sub(r'\b(FROM|JOIN)(\s+)([A-Z_][A-Z0-9_]*)\s*\(', lambda m: m.group(1) + m.group(2) + 'FUNC_PLACEHOLDER(', sql_clean, flags=re.IGNORECASE)
    cte_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\(', sql_clean, re.IGNORECASE)
    ref_tables = re.findall(r'(?:FROM|JOIN)\s+(?:[a-zA-Z_][a-zA-Z0-9_]*\.)?([a-zA-Z_][a-zA-Z0-9_]*)', sql_clean, re.IGNORECASE)
    # PostgreSQL 내장 집합 반환 함수 / 서브쿼리 예약어 등 테이블명으로 오인 방지
    PG_SET_FUNCTIONS = {
        'generate_series', 'unnest', 'json_array_elements', 'jsonb_array_elements',
        'json_each', 'jsonb_each', 'json_object_keys', 'jsonb_object_keys',
        'regexp_matches', 'regexp_split_to_table', 'string_to_table',
        'pg_catalog', 'information_schema', 'lateral',
    }
    skip_aliases = {'_sub', 'sr', 'cum', 'cte', 'sub', 't', 'a', 'b', 'extract_placeholder', 'func_placeholder'}
    skip_aliases.update(PG_SET_FUNCTIONS)
    skip_aliases.update([name.lower() for name in cte_names])

    # column_map 키 정규화 (스키마 포함된 이름 추출)
    column_map_tables = set()
    for key in column_map.keys():
        # 'inventory_mgmt.sales_orders' → 'sales_orders' 추출
        table_name = key.split('.')[-1] if '.' in key else key
        column_map_tables.add(table_name.lower())

    # 3-1. 물리 테이블 간 직접 CROSS JOIN 경고
    # CROSS JOIN 대상이 CTE/서브쿼리가 아닌 실제 물리 테이블이면 위험
    if cross_join_cnt > 0:
        cte_name_set = {n.lower() for n in cte_names}
        cross_join_targets = re.findall(
            r'\bCROSS\s+JOIN\s+(?:[a-zA-Z_][a-zA-Z0-9_]*\.)?([a-zA-Z_][a-zA-Z0-9_]*)',
            sql, re.IGNORECASE
        )
        for target in cross_join_targets:
            if target.lower() not in cte_name_set and target.lower() in column_map_tables:
                errors.append(
                    f"물리 테이블 '{target}'에 직접 CROSS JOIN 감지. "
                    f"집계 CTE를 먼저 만든 뒤 CROSS JOIN하세요."
                )
                strategy = "logic"

    for tbl in ref_tables:
        if tbl.lower() not in column_map_tables and tbl.lower() not in skip_aliases:
            errors.append(f"테이블 '{tbl}' 없음. 유효: {list(column_map.keys())}")
            strategy = "table_missing"
    
    # 5. 컬럼 소속 검증
    col_valid, col_reason = validate_column_ownership(sql_normalized, column_map)
    if not col_valid:
        errors.append(col_reason)
        strategy = "column_missing"
    
    # 6. 불필요한 JOIN 감지 (CROSS JOIN 별칭은 dot notation 없이 쓰는 경우가 많아 제외)
    # ✅ 마지막 캡처 그룹으로 alias만 추출 (이전 코드는 전체 매치를 저장해서 비교가 항상 실패했음)
    cross_join_aliases = set()
    for _m in re.finditer(
        r'\bCROSS\s+JOIN\s+(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)(?:\.)?(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?("?[a-zA-Z_][a-zA-Z0-9_]*"?)',
        sql, re.IGNORECASE
    ):
        cross_join_aliases.add(_m.group(1).strip('"').lower())
    join_aliases = re.findall(
        r'JOIN\s+(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)(?:\.)?(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)\s+(?:AS\s+)?(?:"[^"]+"|[a-zA-Z_][a-zA-Z0-9_]*)',
        sql, re.IGNORECASE
    )
    # join_aliases returns full token, normalize to alias
    join_aliases = [a.strip('"').split()[-1].strip('"') for a in join_aliases]
    for alias in join_aliases:
        if alias.upper() in ('ON', 'USING') or alias.lower() in cross_join_aliases:
            continue
        usage = re.findall(rf'\b{re.escape(alias)}\.', sql, re.IGNORECASE)
        if not usage:
            errors.append(f"불필요한 JOIN: '{alias}' 미사용")
    
    # 7. JOIN 키 매핑 검증 (schema.table 형식 지원)
    # alias_map은 이미 추출되어 있음
    for on_clause in re.finditer(
        r'ON\s+(?:"?([a-zA-Z_][a-zA-Z0-9_]*)"?)\.(?:"?([a-zA-Z_][a-zA-Z0-9_]*)"?)\s*=\s*(?:"?([a-zA-Z_][a-zA-Z0-9_]*)"?)\.(?:"?([a-zA-Z_][a-zA-Z0-9_]*)"?)',
        sql, re.IGNORECASE
    ):
        a1, c1, a2, c2 = on_clause.groups()
        t1, t2 = alias_map.get(a1.lower()), alias_map.get(a2.lower())
        
        # self-join은 검사 대상에서 제외
        if t1 and t2 and t1 != t2:
            pair = frozenset([t1, t2])
            expected_key = VALID_JOINS.get(pair)
            
            if expected_key:
                if c1.lower() != expected_key or c2.lower() != expected_key:
                    errors.append(f"잘못된 JOIN: '{t1}'과 '{t2}'는 '{expected_key}' 컬럼으로 연결해야 함")
                    strategy = "logic"
    
    if errors:
        return False, " | ".join(errors), strategy
    
    return True, "", "none"


def get_retry_strategy(error_msg: str, column_map: dict) -> dict:
    """에러 메시지로부터 재시도 전략 반환"""
    err_lower = error_msg.lower()
    
    if "does not exist" in err_lower and "column" in err_lower:
        col_match = re.search(r'column "?(\w+)"?', error_msg, re.IGNORECASE)
        missing = col_match.group(1) if col_match else "unknown"
        found_in = [t for t, cols in column_map.items()
                   if missing.lower() in [c.lower() for c in cols]]
        hint = f"'{missing}' 컬럼은 {found_in[0] if found_in else '?'} 테이블 소속"
        if found_in:
            hint += f". JOIN {found_in[0]} 후 {found_in[0]}.{missing}로 참조"
        return {"strategy": "column_missing", "hint": hint}
    
    if "relation" in err_lower and "does not exist" in err_lower:
        tbl_match = re.search(r'relation "?(\w+)"?', error_msg, re.IGNORECASE)
        missing = tbl_match.group(1) if tbl_match else "unknown"
        return {"strategy": "table_missing",
                "hint": f"테이블 '{missing}' 없음. 유효: {list(column_map.keys())}"}
    
    if "syntax error" in err_lower:
        return {"strategy": "syntax",
                "hint": "SQL 단순화: TO_DATE 중첩 금지. EXTRACT(YEAR)=-연도 사용."}
    
    if "timeout" in err_lower or "canceling" in err_lower:
        return {"strategy": "timeout",
                "hint": "타임아웃: LIMIT 축소, WHERE 범위 추가, CTE로 분리"}
    
    if "group by" in err_lower or "aggregate" in err_lower:
        return {"strategy": "logic",
                "hint": "GROUP BY 오류: SELECT의 모든 비집계 컬럼 포함"}
    
    return {"strategy": "unknown", "hint": error_msg[:300]}


def clean_sql(raw: str) -> str:
    """LLM 출력에서 순수 SQL만 추출"""
    # 터미널 이스케이프 코드 제거
    raw = re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', raw)
    raw = re.sub(r'\033\[[0-9;]*[mGKHF]', '', raw)
    raw = re.sub(r'←\[[0-9;]*[mGKHF]', '', raw)
    
    # 마크다운 코드블록에서 SQL 추출
    match = re.search(r'```(?:sql)?\s*(.*?)\s*```', raw, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        sql = re.sub(r'^```|```$', '', raw.strip(), flags=re.MULTILINE).strip()
    
    # 세미콜론 이후 문자 제거
    sql = sql.split(';')[0].strip()
    
    logger.debug(f"SQL 정제 완료:\n{sql}")
    return sql
