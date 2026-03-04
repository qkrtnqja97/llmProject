# -*- coding: utf-8 -*-
"""
api_llm 패키지
구조화된 엔터프라이즈 AI 에이전트 시스템
"""

__version__ = "1.0.0"
__author__ = "Enterprise AI Team"

from .log_config.logger_config import setup_logging, get_logger

# 패키지 초기화
setup_logging()

__all__ = [
    "get_logger",
    "setup_logging",
]
