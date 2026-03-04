from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class TranslateRequest(BaseModel):
    text: str = Field(..., description="번역할 텍스트")
    source: str = Field(default="ko")
    target: str = Field(default="en")
    use_llm: bool = Field(default=True)
    glossary: Optional[Dict[str, str]] = Field(default=None)

class BatchTranslateRequest(BaseModel):
    texts: List[str]
    source: str = "ko"
    target: str = "en"
    use_llm: bool = True
    glossary: Optional[Dict[str, str]] = None

class MultiTranslateRequest(BaseModel):
    text: str
    source: str = "ko"
    targets: List[str]
    use_llm: bool = True
    glossary: Optional[Dict[str, str]] = None

class EmailTranslateRequest(BaseModel):
    from_addr: Optional[str] = None
    subject: Optional[str] = None
    body: str
    source: str = "en"
    target: str = "ko"
    use_llm: bool = True

class TranslateResponse(BaseModel):
    translation: str
    rough: str
    refined: bool