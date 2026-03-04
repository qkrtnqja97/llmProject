import os
import requests
from io import BytesIO
from typing import Optional, Dict, Tuple
from deep_translator import GoogleTranslator
from docx import Document as DocxDocument

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

LANGUAGES = {
    "ko": "한국어", "en": "영어", "ja": "일본어", "zh-CN": "중국어(간체)",
    "zh-TW": "중국어(번체)", "es": "스페인어", "fr": "프랑스어", "de": "독일어", "ru": "러시아어"
}

class TranslateService:
    @staticmethod
    def translate_rough(text: str, source: str, target: str) -> str:
        return GoogleTranslator(source=source, target=target).translate(text)

    @staticmethod
    def refine_with_ollama(original: str, rough: str, source: str, target: str, glossary: Optional[Dict] = None) -> Optional[str]:
        source_name = LANGUAGES.get(source, source)
        target_name = LANGUAGES.get(target, target)
        
        glossary_text = ""
        if glossary:
            items = "\n".join([f"- {k} → {v}" for k, v in glossary.items()])
            glossary_text = f"\n[용어집 지시]:\n{items}\n"

        prompt = f"""{glossary_text}
당신은 전문 번역가입니다. 다음 기계 번역을 참고하여 {source_name} 원문을 {target_name}으로 자연스럽게 교정하세요.
문맥을 고려하여 부드럽게 다듬고, 결과만 출력하세요.

원문: {original}
기계 번역: {rough}
개선된 번역:"""

        try:
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=60
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except:
            return None

    @classmethod
    def do_translate(cls, text: str, source: str, target: str, use_llm: bool, glossary: Optional[Dict] = None) -> Tuple[str, str, bool]:
        if not text.strip():
            return "", "", False
        rough = cls.translate_rough(text, source, target)
        if use_llm:
            refined = cls.refine_with_ollama(text, rough, source, target, glossary)
            return (refined, rough, True) if refined else (rough, rough, False)
        return rough, rough, False

    @staticmethod
    def extract_text(content: bytes, filename: str) -> str:
        ext = filename.split('.')[-1].lower()
        if ext == "txt":
            return content.decode("utf-8", errors="replace")
        elif ext in ("docx", "doc"):
            doc = DocxDocument(BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        raise ValueError(f"지원하지 않는 형식: {ext}")