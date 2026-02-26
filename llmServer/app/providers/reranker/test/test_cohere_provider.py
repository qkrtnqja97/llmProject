from app.providers.reranker.cohere_provider import CohereRerankerProvider
from app.core.config import settings

if __name__ == "__main__":

    print("🚀 리랭커 실제 호출 테스트")
    print("🔑 key 읽힘?:", bool(settings.COHERE_API_KEY))

    api_key = settings.COHERE_API_KEY
    if not api_key:
        raise ValueError("환경변수 COHERE_API_KEY 설정 필요")

    reranker = CohereRerankerProvider(api_key=api_key)

    query = "network switch chip"

    docs = [
        "BCM5650 is a high-performance network switch chip",
        "Apple is a fruit",
        "Electronic components distributor company",
        "Temperature sensor IC",
    ]

    scores = reranker.score(query, docs)

    print("\nQuery:", query)
    print("\nDocs:")
    for d in docs:
        print("-", d)

    print("\nScores:")
    for s in scores:
        print(s)