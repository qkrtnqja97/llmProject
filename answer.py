import os
from google import genai
from llm_chromadb import get_chroma_client
from embed import get_embeddings_batch # 일관성을 위해 batch 함수 사용



# [공통 설정]
# 모델 선언 (성능과 속도의 균형이 좋은 2.5 Flash 추천 , 업그레이드는 gemini-3-flash쓰기)
MODEL_NAME = 'gemini-2.5-flash' 



def ask_question():
    # [Step 1] 시스템 연결
    print("\n🚀 [Step 1] 시스템 연결 중...")
    chroma_client = get_chroma_client()
    if not chroma_client: return
    collection = chroma_client.get_collection(name="jw_gemini_collection")
    print("✅ DB 및 컬렉션 연결 완료")

    # [Step 2] 사용자 질문 입력
    print("\n🚀 [Step 2] 질문을 입력받습니다.")
    user_query = input("💬 질문을 입력하세요: ")
    
    try:
        # [Step 3] 검색
        query_vector = get_embeddings_batch([user_query])[0]
        
        # include에 'documents'만 명시하여 가져옴
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3,
            include=['documents']
        )
        
        # 검색된 원문 텍스트(documents) 추출
        retrieved_context = "\n".join(results['documents'][0])
        
        # [Step 4] Gemini 답변 생성 (사용자 모델 설정 유지)
        full_prompt = f"재고 정보:\n{retrieved_context}\n\n질문: {user_query}"
        
        # 사용자님의 환경에 맞는 클라이언트 호출 방식 유지
        from google import genai
        from dotenv import load_dotenv
        load_dotenv("Plaintext.env")
        api_key = os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
        )

        print("\n" + "="*50)
        print(f"🤖 답변:\n{response.text}")
        print("="*50)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    ask_question()