"""
Hugging Face Daily Papers Newsletter Configuration
한국어 뉴스레터 설정을 관리합니다.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """뉴스레터 설정"""
    
    # Hugging Face 설정
    HF_PAPERS_URL: str = "https://huggingface.co/papers"
    HF_PAPERS_API: str = "https://huggingface.co/api/papers/daily"
    
    # 번역/요약 서비스 (basic, openai, minimax)
    # .env 파일에서 TRANSLATION_MODE로 변경 가능
    TRANSLATION_MODE: str = "basic"
    
    # OpenAI 설정
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # MiniMax API 설정
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_GROUP_ID: Optional[str] = None
    MINIMAX_MODEL: str = "MiniMax-Text-01"
    
    # 이메일 설정
    EMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SENDER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_RECIPIENTS: list = None
    
    # 뉴스레터 설정
    NEWSLETTER_LANGUAGE: str = "ko"
    PAPERS_PER_DAY: int = 10
    INCLUDE_ABSTRACT: bool = True
    INCLUDE_TRANSLATION: bool = True
    
    def __post_init__(self):
        if self.EMAIL_RECIPIENTS is None:
            self.EMAIL_RECIPIENTS = []
    
    @classmethod
    def from_env(cls):
        """환경 변수에서 설정 로드
        
        .env 파일이나 환경 변수에서 설정을 읽어옵니다.
        설정优先级: 환경 변수 > 기본값
        """
        return cls(
            TRANSLATION_MODE=os.getenv("TRANSLATION_MODE", "basic"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            MINIMAX_API_KEY=os.getenv("MINIMAX_API_KEY"),
            MINIMAX_GROUP_ID=os.getenv("MINIMAX_GROUP_ID"),
            MINIMAX_MODEL=os.getenv("MINIMAX_MODEL", "MiniMax-Text-01"),
            EMAIL_SENDER=os.getenv("EMAIL_SENDER"),
            EMAIL_PASSWORD=os.getenv("EMAIL_PASSWORD"),
            EMAIL_RECIPIENTS=os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []
        )
