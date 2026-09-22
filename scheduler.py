"""
Main Script for HF Papers Newsletter
자동으로 뉴스레터를 실행하고 이메일을 발송합니다.
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

from crawler import HuggingFacePapersCrawler
from translator import get_translator
from newsletter import NewsletterGenerator, EmailSender
from filter import PaperFilter, filter_robotics_papers, FilterConfig
from config import Config


def run_newsletter(
    config: Config,
    date: str = None,
    max_papers: int = 10,
    dry_run: bool = False,
    output_file: str = None,
    filter_type: str = None,
    custom_keywords: list = None
):
    """
    뉴스레터 실행
    
    Args:
        config: 설정 객체
        date: 날짜 (YYYY-MM-DD), None이면 오늘
        max_papers: 최대 논문 수
        dry_run: True면 이메일 발송 없이 미리보기만
        output_file: 출력 파일 경로 (None이면 콘솔 출력)
        filter_type: 필터 타입 (None, robotics, physical_ai, realworld, vision, multimodal, robotics_full)
        custom_keywords: 커스텀 필터링 키워드 리스트
    """
    print("=" * 60)
    print("🤗 Hugging Face Daily Papers - 한국어 뉴스레터")
    print("=" * 60)
    
    if date:
        print(f"📅 날짜: {date}")
    else:
        print(f"📅 날짜: {datetime.now().strftime('%Y-%m-%d')}")
    
    print(f"📊 최대 논문 수: {max_papers}")
    
    # 필터 정보
    if filter_type:
        filter_obj = PaperFilter()
        if filter_type == "robotics_full":
            print("🎯 필터: 로보틱스 + 피지컬 AI + 리얼월드")
        elif filter_type in PaperFilter.PRESETS:
            print(f"🎯 필터: {PaperFilter.PRESETS[filter_type]['name']}")
        else:
            print(f"🎯 필터: 커스텀 ({len(custom_keywords or [])}개 키워드)")
    elif custom_keywords:
        print(f"🎯 필터: 커스텀 ({len(custom_keywords)}개 키워드)")
    else:
        print("🎯 필터: 없음 (전체 논문)")
    
    print()
    
    # 1. 논문 가져오기
    print("1️⃣ Hugging Face에서 논문 가져오는 중...")
    crawler = HuggingFacePapersCrawler()
    
    try:
        papers = crawler.fetch_daily_papers(date)
        
        if not papers:
            print("❌ 논문을 가져오지 못했습니다.")
            return False
        
        print(f"   ✅ {len(papers)}개의 논문을 찾았습니다!")
        
    finally:
        crawler.close()
    
    # 1.5 필터링
    if filter_type or custom_keywords:
        print("\n1.5️⃣ 논문 필터링 중...")
        
        if filter_type == "robotics_full":
            # 로보틱스 + 피지컬 AI + 리얼월드
            filtered = filter_robotics_papers(papers)
        elif filter_type:
            # 사전 정의된 필터
            if filter_type in PaperFilter.PRESETS:
                preset = PaperFilter.PRESETS[filter_type]
                filter_config = FilterConfig(
                    include_keywords=preset["include"],
                    exclude_keywords=preset.get("exclude", set())
                )
                filter_obj = PaperFilter(filter_config)
                filtered = filter_obj.filter_papers(papers)
            else:
                filtered = papers
        elif custom_keywords:
            # 커스텀 키워드
            filter_config = FilterConfig(
                include_keywords=set(custom_keywords)
            )
            filter_obj = PaperFilter(filter_config)
            filtered = filter_obj.filter_papers(papers)
        else:
            filtered = papers
        
        print(f"   ✅ {len(filtered)}/{len(papers)}개의 논문이 필터링됨")
        papers = filtered
    
    # 2. 번역
    print("\n2️⃣ 논문 번역 중...")
    translator = get_translator(
        mode=config.TRANSLATION_MODE,
        api_key=config.openai_api_key,
        model=config.openai_model,
        minimax_api_key=config.MINIMAX_API_KEY,
        minimax_group_id=config.MINIMAX_GROUP_ID,
        minimax_model=config.MINIMAX_MODEL
    )
    print(f"   ✅ 번역 모드: {config.TRANSLATION_MODE}")
    
    # 3. 뉴스레터 생성
    print("\n3️⃣ 뉴스레터 생성 중...")
    generator = NewsletterGenerator(translator)
    content = generator.generate(papers, max_papers=max_papers)
    
    print(f"   ✅ {content.total_count}개의 논문으로 뉴스레터 생성 완료!")
    
    # 4. 출력
    print("\n4️⃣ 출력 처리 중...")
    
    html_content = generator.to_html(content)
    text_content = generator.to_text(content)
    
    if output_file:
        # 파일로 저장
        output_path = Path(output_file)
        
        if output_path.suffix == '.html':
            output_path.write_text(html_content, encoding='utf-8')
        elif output_path.suffix == '.txt':
            output_path.write_text(text_content, encoding='utf-8')
        else:
            # 둘 다 저장
            html_path = output_path.with_suffix('.html')
            txt_path = output_path.with_suffix('.txt')
            html_path.write_text(html_content, encoding='utf-8')
            txt_path.write_text(text_content, encoding='utf-8')
            print(f"   ✅ HTML: {html_path}")
            print(f"   ✅ TXT: {txt_path}")
            output_file = str(output_path)
        
        print(f"   ✅ 파일 저장 완료: {output_file}")
    else:
        # 콘솔에 미리보기
        print("\n--- HTML 미리보기 (첫 1000자) ---")
        print(html_content[:1000])
        print("\n... (이하 생략) ...\n")
    
    # 5. 이메일 발송
    if not dry_run and config.EMAIL_RECIPIENTS:
        print("\n5️⃣ 이메일 발송 중...")
        sender = EmailSender(
            smtp_server=config.EMAIL_SMTP_SERVER,
            smtp_port=config.EMAIL_SMTP_PORT,
            sender=config.EMAIL_SENDER,
            password=config.EMAIL_PASSWORD
        )
        
        success = sender.send_newsletter(
            recipients=config.EMAIL_RECIPIENTS,
            content=content
        )
        
        if success:
            print("\n✅ 모든 작업이 완료되었습니다!")
        else:
            print("\n⚠️ 이메일 발송에 실패했지만 다른 작업은 완료되었습니다.")
            return False
    else:
        if dry_run:
            print("\n⚠️ Dry-run 모드: 이메일 발송 건너뜀")
        else:
            print("\n⚠️ 수신자가 설정되지 않음: 이메일 발송 건너뜀")
    
    print("\n" + "=" * 60)
    return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Hugging Face Daily Papers 한국어 뉴스레터 생성기"
    )
    
    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="날짜 (YYYY-MM-DD 형식, 기본값: 오늘)"
    )
    
    parser.add_argument(
        "--max-papers", "-n",
        type=int,
        default=10,
        help="포함할 최대 논문 수 (기본값: 10)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="이메일 발송 없이 미리보기만 실행"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="출력 파일 경로"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="설정 파일 경로"
    )
    
    parser.add_argument(
        "--openai",
        action="store_true",
        help="OpenAI GPT를 사용한 번역 (OPENAI_API_KEY 필요)"
    )
    
    parser.add_argument(
        "--minimax",
        action="store_true",
        help="MiniMax API를 사용한 번역 (MINIMAX_API_KEY 필요)"
    )
    
    # 필터 옵션
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        "--robotics",
        action="store_true",
        help="로보틱스 관련 논문만 필터링"
    )
    filter_group.add_argument(
        "--physical-ai",
        action="store_true",
        help="피지컬 AI 관련 논문만 필터링"
    )
    filter_group.add_argument(
        "--realworld",
        action="store_true",
        help="리얼월드 관련 논문만 필터링"
    )
    filter_group.add_argument(
        "--robotics-full",
        action="store_true",
        help="로보틱스 + 피지컬 AI + 리얼월드 관련 논문 필터링"
    )
    filter_group.add_argument(
        "--vision",
        action="store_true",
        help="컴퓨터 비전 관련 논문만 필터링"
    )
    filter_group.add_argument(
        "--multimodal",
        action="store_true",
        help="멀티모달 관련 논문만 필터링"
    )
    filter_group.add_argument(
        "--vla",
        action="store_true",
        help="VLA (Vision-Language-Action) 관련 논문만 필터링"
    )
    filter_group.add_argument(
        "--keywords",
        type=str,
        nargs="+",
        help="커스텀 키워드로 필터링 (예: --keywords robot arm manipulation)"
    )
    
    args = parser.parse_args()
    
    # 설정 로드
    if args.config:
        # 설정 파일에서 로드 (나중에 구현)
        config = Config.from_env()
    else:
        config = Config.from_env()
    
    # 번역 모드 설정
    if args.minimax:
        config.TRANSLATION_MODE = "minimax"
    elif args.openai:
        config.TRANSLATION_MODE = "openai"
    
    # 필터 타입 결정
    filter_type = None
    custom_keywords = None
    
    if args.robotics_full:
        filter_type = "robotics_full"
    elif args.robotics:
        filter_type = "robotics"
    elif args.physical_ai:
        filter_type = "physical_ai"
    elif args.realworld:
        filter_type = "realworld"
    elif args.vision:
        filter_type = "vision"
    elif args.multimodal:
        filter_type = "multimodal"
    elif args.vla:
        filter_type = "vla"
    elif args.keywords:
        custom_keywords = args.keywords
    
    # 실행
    success = run_newsletter(
        config=config,
        date=args.date,
        max_papers=args.max_papers,
        dry_run=args.dry_run,
        output_file=args.output,
        filter_type=filter_type,
        custom_keywords=custom_keywords
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
