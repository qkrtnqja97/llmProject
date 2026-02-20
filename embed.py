# embed.py

# -*- coding: utf-8 -*-
import os
import voyageai
from dotenv import load_dotenv

# [기능 설명] .env 파일에서 Voyage AI API 키를 로드합니다.
load_dotenv("Plaintext.env")
api_key = os.getenv("VOYAGE_API_KEY")

# [기능 설명] Voyage AI 클라이언트를 초기화합니다.
# API 키가 없을 경우를 대비해 예외 처리를 준비합니다.
vo = voyageai.Client(api_key=api_key) if api_key else None

def get_embeddings_batch(text_list, input_type="document"):
    """
    [기능 설명] 문장 리스트를 받아 Voyage AI 벡터(숫자 리스트) 리스트를 반환합니다.
    ChromaDB 적재 시에는 input_type="document", 검색 시에는 "query"를 사용하세요.
    """
    if not vo:
        raise Exception("❌ VOYAGE_API_KEY가 설정되지 않았거나 클라이언트 초기화에 실패했습니다.")
    
    if not text_list:
        return []

    try:
        # [기능 설명] Voyage AI의 다국어 특화 모델을 사용하여 임베딩을 생성합니다.
        # 한국어 검색 성능이 매우 뛰어난 'voyage-multilingual-2' 모델을 권장합니다.
        result = vo.embed(
            text_list, 
            model="voyage-multilingual-2", 
            input_type=input_type
        )
        
        # [기능 설명] 결과 객체에서 임베딩 리스트(embeddings)를 반환합니다.
        return result.embeddings
        
    except Exception as e:
        # [기능 설명] Rate Limit(429)이나 API 오류 발생 시 상위 호출부로 에러를 전달합니다.
        print(f"⚠️ Voyage AI 임베딩 생성 중 오류 발생: {e}")
        raise e

if __name__ == "__main__":
    # 간단한 테스트 코드
    test_text = ["안녕하세요, 재고 관리 시스템입니다."]
    try:
        vec = get_embeddings_batch(test_text)
        print(f"✅ 테스트 성공! 벡터 차원 수: {len(vec[0])}")
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")