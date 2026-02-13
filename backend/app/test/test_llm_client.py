# backend/app/test/test_llm_client.py

import os
import requests

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:9000")

def llm_health_check() -> dict:
    res = requests.get(
        f"{LLM_BASE_URL}/health",
        timeout=5,
    )
    res.raise_for_status()
    return res.json()
