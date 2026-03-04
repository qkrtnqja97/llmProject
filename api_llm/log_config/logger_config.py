# -*- coding: utf-8 -*-
"""
로깅 설정 모듈
- 애플리케이션 로그 (app.log)
- 로컬 모델 학습 로그 (training.log)
- 구조화된 로깅으로 로컬 모델 학습 추적 가능
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from api_llm.config import LOGGING_CONFIG


def setup_logging():
    """메인 애플리케이션 로그 설정"""
    
    log_level = getattr(logging, LOGGING_CONFIG["LOG_LEVEL"], logging.INFO)
    log_file = LOGGING_CONFIG["LOG_FILE"]
    log_format = LOGGING_CONFIG["LOG_FORMAT"]
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 포맷터 생성
    formatter = logging.Formatter(log_format)
    
    # 파일 핸들러 (메인 로그) - UTF-8 명시
    if LOGGING_CONFIG["ENABLE_FILE_HANDLER"]:
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=LOGGING_CONFIG["LOG_MAX_BYTES"],
            backupCount=LOGGING_CONFIG["LOG_BACKUP_COUNT"],
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    if LOGGING_CONFIG["ENABLE_STREAM_HANDLER"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)
    
    return root_logger


def setup_training_logger():
    """로컬 모델 학습용 별도 로거 설정
    
    로컬 모델 학습 중 메트릭, 손실값, 평가 지표를 별도 파일에 기록
    """
    
    training_logger = logging.getLogger("training")
    training_logger.setLevel(logging.DEBUG)
    
    # 기존 핸들러 제거
    for handler in training_logger.handlers[:]:
        training_logger.removeHandler(handler)
    
    # 학습 로그 파일 핸들러
    training_log_file = LOGGING_CONFIG["TRAINING_LOG_FILE"]
    training_handler = RotatingFileHandler(
        filename=training_log_file,
        maxBytes=LOGGING_CONFIG["LOG_MAX_BYTES"],
        backupCount=LOGGING_CONFIG["LOG_BACKUP_COUNT"],
        encoding="utf-8"
    )
    
    # 상세 포맷 (학습 메트릭 추적용)
    training_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    training_handler.setFormatter(training_format)
    training_logger.addHandler(training_handler)
    
    return training_logger


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거 반환"""
    return logging.getLogger(name)


def get_training_logger() -> logging.Logger:
    """학습 전용 로거 반환"""
    return logging.getLogger("training")


# 모듈 초기화 시 로깅 설정
setup_logging()
setup_training_logger()

# 샘플 용도의 기본 로거
logger = get_logger(__name__)
