"""
Translation Module for Korean Newsletter
한국어 번역 및 요약 모듈
"""

import re
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class TranslatedPaper:
    """번역된 논문 정보"""
    original_title: str
    korean_title: str
    original_summary: str
    korean_summary: str
    key_points: list  # 핵심 포인트 (한국어)
    korean_authors: list  # 한국어 저자명


class BasicTranslator:
    """기본 번역기 (사전 기반 + 규칙)"""
    
    def __init__(self):
        # 일반적인 AI/ML 용어 사전
        self.tech_terms = {
            # 모델 & 아키텍처
            "model": "모델",
            "models": "모델",
            "large language model": "대규모 언어 모델",
            "llm": "대규모 언어 모델",
            "llms": "대규모 언어 모델",
            "neural network": "신경망",
            "network": "네트워크",
            "transformer": "트랜스포머",
            "attention": "어텐션",
            "self-attention": "셀프 어텐션",
            "encoder": "인코더",
            "decoder": "디코더",
            "embedding": "임베딩",
            "token": "토큰",
            "tokens": "토큰",
            
            # 학습 & 최적화
            "training": "학습",
            "fine-tuning": "파인튜닝",
            "fine tuning": "파인튜닝",
            "pre-training": "사전학습",
            "pre-training": "사전학습",
            "learning": "학습",
            "optimization": "최적화",
            "optimizer": "옵티마이저",
            "gradient": "그래디언트",
            "backpropagation": "역전파",
            "loss": "손실",
            "loss function": "손실 함수",
            
            # 데이터
            "dataset": "데이터셋",
            "datasets": "데이터셋",
            "data": "데이터",
            "training data": "학습 데이터",
            "test data": "테스트 데이터",
            "benchmark": "벤치마크",
            "evaluation": "평가",
            
            # 성능 & 메트릭스
            "accuracy": "정확도",
            "performance": "성능",
            "performance": "성능",
            "efficiency": "효율성",
            "efficiency": "효율성",
            "speed": "속도",
            "latency": "지연시간",
            "throughput": "처리량",
            "robustness": "강건성",
            "generalization": "범용화",
            
            # AI 연구 분야
            "nlp": "자연어처리",
            "natural language processing": "자연어처리",
            "computer vision": "컴퓨터 비전",
            "cv": "컴퓨터 비전",
            "reinforcement learning": "강화학습",
            "generative": "생성형",
            "multimodal": "멀티모달",
            "foundation model": "기초 모델",
            
            # 테크닉 & 방법론
            "rag": "검색 증강 생성",
            "retrieval-augmented generation": "검색 증강 생성",
            "chain-of-thought": "생각의 연쇄",
            "prompting": "프롬프팅",
            "prompt": "프롬프트",
            "in-context learning": "문맥 내 학습",
            "few-shot": "퓨샷",
            "zero-shot": "제로샷",
            
            # 기술적 용어
            "inference": "추론",
            "deployment": "배포",
            "quantization": "양자화",
            "compression": "압축",
            "pruning": "가지치기",
            "distillation": "증류",
            "knowledge distillation": "지식 증류",
            
            # 기타
            "state-of-the-art": "최첨단",
            "sota": "최첨단",
            "breakthrough": "획기적",
            "novel": "새로운",
            "proposed": "제안된",
            "approach": "접근법",
            "method": "방법",
            "framework": "프레임워크",
            "architecture": "아키텍처",
            "algorithm": "알고리즘",
            "system": "시스템",
            "platform": "플랫폼",
            "application": "응용",
            "task": "작업",
            "capability": "능력",
            "ability": "능력",
            
            # 평가 및 실험
            "experiment": "실험",
            "experiments": "실험",
            "result": "결과",
            "results": "결과",
            "significant": "상당한",
            "improvement": "개선",
            "achieve": "달성",
            "outperform": "능가",
            "baseline": "베이스라인",
            
            # 조직/기술
            "ai": "인공지능",
            "ml": "머신러닝",
            "dl": "딥러닝",
            "gpu": "GPU",
            "cpu": "CPU",
            
            # 텍스트 관련
            "text": "텍스트",
            "image": "이미지",
            "video": "비디오",
            "audio": "오디오",
            "speech": "음성",
            "language": "언어",
            "translation": "번역",
            "summarization": "요약",
            "generation": "생성",
            "understanding": "이해",
            "recognition": "인식",
        }
        
        # 불용어 (번역 시 그대로 유지)
        self.stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
            "into", "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once", "here",
            "there", "when", "where", "why", "how", "all", "each", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "just",
            "and", "but", "or", "because", "as", "until", "while",
            "this", "that", "these", "those", "it", "its",
            "we", "you", "they", "he", "she", "him", "her", "his",
            "i", "me", "my", "your", "yours", "our", "ours", "their", "theirs"
        }
    
    def translate_to_korean(self, text: str) -> str:
        """영어 텍스트를 한국어로 번역"""
        if not text:
            return ""
        
        result = text
        
        # 기술 용어 먼저 치환 (긴 것부터)
        sorted_terms = sorted(self.tech_terms.items(), key=lambda x: len(x[0]), reverse=True)
        for eng, kor in sorted_terms:
            result = re.sub(r'\b' + re.escape(eng) + r'\b', kor, result, flags=re.IGNORECASE)
        
        # 기본적인 영어->한국어 변환 (간단한 패턴)
        # 이 부분은 실제로는 더 정교한 NLP 모델이 필요
        
        return result
    
    def translate_paper(self, title: str, summary: str, authors: list) -> TranslatedPaper:
        """논문 전체 번역"""
        korean_title = self.translate_to_korean(title)
        korean_summary = self.translate_to_korean(summary)
        
        # 핵심 포인트 추출
        key_points = self._extract_key_points(korean_summary)
        
        # 저자명 (보통 그대로 유지하거나, 성과름만 변환)
        korean_authors = authors  # 저자명은 그대로 유지
        
        return TranslatedPaper(
            original_title=title,
            korean_title=korean_title,
            original_summary=summary,
            korean_summary=korean_summary,
            key_points=key_points,
            korean_authors=korean_authors
        )
    
    def _extract_key_points(self, text: str) -> list:
        """한국어 텍스트에서 핵심 포인트 추출"""
        points = []
        
        # 문장 분리
        sentences = re.split(r'[.。]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 20 and len(sent) < 200:  # 적절한 길이의 문장
                # 핵심 키워드 확인
                keywords = ["제안", "새로운", "개발", "성능", "개선", "달성", "효과", "방법", "모델"]
                if any(kw in sent for kw in keywords):
                    points.append(sent)
        
        return points[:3]  # 최대 3개
    
    def format_korean_summary(self, summary: str, max_length: int = 500) -> str:
        """한국어 요약 포맷팅"""
        korean = self.translate_to_korean(summary)
        
        if len(korean) > max_length:
            # 문장 단위로 자르기
            sentences = korean.split("다.")
            result = []
            current_length = 0
            
            for sent in sentences:
                if current_length + len(sent) + 2 > max_length:
                    break
                result.append(sent + "다.")
                current_length += len(sent) + 2
            
            return "".join(result)
        
        return korean


class OpenAITranslator:
    """OpenAI GPT를 사용한 번역기"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.client = None  # 나중에 초기화
    
    def _init_client(self):
        """OpenAI 클라이언트 초기화"""
        try:
            from openai import OpenAI
            if self.client is None:
                self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            print("OpenAI 라이브러리가 설치되지 않았습니다. pip install openai")
            return False
        return True
    
    def translate_with_gpt(self, text: str, target_lang: str = "Korean") -> str:
        """GPT를 사용한 번역"""
        if not self._init_client():
            return text
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a professional translator specializing in AI/ML research papers.
Translate the following English text to {target_lang}.
Maintain the technical accuracy of AI/ML terminology.
Keep brand names, model names, and proper nouns in English.
"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Translation Error: {e}")
            return text
    
    def translate_paper(self, title: str, summary: str, authors: list) -> TranslatedPaper:
        """논문 전체 번역 (GPT 사용)"""
        korean_title = self.translate_with_gpt(title)
        korean_summary = self.translate_with_gpt(summary)
        
        # GPT에게 핵심 포인트 추출 요청
        points_prompt = f"""다음 연구 요약에서 핵심 포인트를 3개 추출해주세요.
각 포인트는 50자 이내로 간결하게 작성해주세요.
요약: {korean_summary}"""
        
        key_points_text = self.translate_with_gpt(points_prompt)
        key_points = [p.strip() for p in key_points_text.split('\n') if p.strip()]
        
        return TranslatedPaper(
            original_title=title,
            korean_title=korean_title,
            original_summary=summary,
            korean_summary=korean_summary,
            key_points=key_points[:3],
            korean_authors=authors
        )


class MiniMaxTranslator:
    """MiniMax API를 사용한 번역기"""
    
    def __init__(self, api_key: str, group_id: str = None, model: str = "MiniMax-Text-01"):
        """
        MiniMax 번역기 초기화
        
        Args:
            api_key: MiniMax API 키
            group_id: MiniMax Group ID
            model: 사용할 모델 (기본값: MiniMax-Text-01)
        """
        self.api_key = api_key
        self.group_id = group_id
        self.model = model
    
    def translate_with_minimax(self, text: str, target_lang: str = "Korean") -> str:
        """MiniMax API를 사용한 번역"""
        import httpx
        import json
        
        if not self.api_key:
            print("MiniMax API 키가 설정되지 않았습니다.")
            return text
        
        try:
            # MiniMax Chat API
            url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"""You are a professional translator specializing in AI/ML research papers.
Translate the following English text to {target_lang}.
Maintain the technical accuracy of AI/ML terminology.
Keep brand names, model names, and proper nouns in English.
Return only the translated text without any explanation."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                return result.get("choices", [{}])[0].get("messages", [{}])[0].get("text", text)
                
        except httpx.HTTPError as e:
            print(f"MiniMax API Error: {e}")
            return text
        except Exception as e:
            print(f"Translation Error: {e}")
            return text
    
    def translate_paper(self, title: str, summary: str, authors: list) -> TranslatedPaper:
        """논문 전체 번역 (MiniMax 사용)"""
        print("   🤖 MiniMax API로 번역 중...")
        
        korean_title = self.translate_with_minimax(title)
        korean_summary = self.translate_with_minimax(summary)
        
        # 핵심 포인트 추출
        points_prompt = f"""다음 연구 요약에서 핵심 포인트를 3개 추출해주세요.
각 포인트는 50자 이내로 간결하게 작성해주세요.
요약: {korean_summary}"""
        
        key_points_text = self.translate_with_minimax(points_prompt)
        key_points = [p.strip() for p in key_points_text.split('\n') if p.strip()]
        
        return TranslatedPaper(
            original_title=title,
            korean_title=korean_title,
            original_summary=summary,
            korean_summary=korean_summary,
            key_points=key_points[:3],
            korean_authors=authors
        )


def get_translator(mode: str = "basic", **kwargs) -> BasicTranslator | OpenAITranslator | MiniMaxTranslator:
    """번역기 팩토리 함수"""
    if mode == "minimax":
        api_key = kwargs.get("minimax_api_key")
        group_id = kwargs.get("minimax_group_id")
        model = kwargs.get("minimax_model", "MiniMax-Text-01")
        return MiniMaxTranslator(api_key, group_id, model)
    elif mode == "openai":
        api_key = kwargs.get("api_key")
        model = kwargs.get("model", "gpt-4o-mini")
        return OpenAITranslator(api_key, model)
    else:
        return BasicTranslator()


# 테스트
if __name__ == "__main__":
    translator = BasicTranslator()
    
    test_text = "We present a novel approach to improve the performance of large language models through retrieval-augmented generation."
    
    print("원문:", test_text)
    print("\n번역:", translator.translate_to_korean(test_text))
