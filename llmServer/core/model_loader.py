# llmServer/core/model_loader.py
# LLM 모델을 로드하는 유틸리티 함수 정의

class MockModel:
    def generate(self, prompt: str) -> str:
        return f"LLM says: {prompt}"

def load_model():
    # 실제로는 여기서 모델 로딩
    return MockModel()
