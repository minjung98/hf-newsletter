"""
Newsletter Generator
한국어 뉴스레터를 생성합니다.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from typing import List
from dataclasses import dataclass

from crawler import Paper
from translator import TranslatedPaper, BasicTranslator


@dataclass
class NewsletterContent:
    """뉴스레터 콘텐츠"""
    date: str
    papers: List[TranslatedPaper]
    total_count: int


class NewsletterGenerator:
    """한국어 뉴스레터 생성기"""
    
    def __init__(self, translator: BasicTranslator = None):
        self.translator = translator or BasicTranslator()
    
    def generate(self, papers: List[Paper], max_papers: int = 10) -> NewsletterContent:
        """논문 목록에서 뉴스레터 콘텐츠 생성"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        translated_papers = []
        for paper in papers[:max_papers]:
            translated = self.translator.translate_paper(
                title=paper.title,
                summary=paper.summary,
                authors=paper.authors
            )
            # 추가 메타데이터 포함
            translated.paper_url = paper.url
            translated.upvotes = paper.upvotes
            translated.organization = paper.organization
            translated.paper_id = paper.paper_id
            translated_papers.append(translated)
        
        return NewsletterContent(
            date=today,
            papers=translated_papers,
            total_count=len(translated_papers)
        )
    
    def to_html(self, content: NewsletterContent) -> str:
        """HTML 형식의 뉴스레터 생성"""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hugging Face Daily Papers - {content.date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #FFD21E 0%, #FF9D0B 100%);
            color: white;
            padding: 30px;
            border-radius: 16px 16px 0 0;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .date-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 20px;
            margin-top: 12px;
            font-size: 14px;
        }}
        
        .content {{
            background: white;
            padding: 24px;
            border-radius: 0 0 16px 16px;
        }}
        
        .paper-card {{
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: box-shadow 0.3s;
        }}
        
        .paper-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .paper-number {{
            display: inline-block;
            width: 28px;
            height: 28px;
            background: #FFD21E;
            color: #333;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-weight: bold;
            font-size: 14px;
            margin-right: 12px;
        }}
        
        .paper-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .paper-title-en {{
            font-size: 14px;
            color: #666;
            font-style: italic;
            margin-bottom: 12px;
        }}
        
        .paper-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 13px;
            color: #666;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .meta-item svg {{
            width: 14px;
            height: 14px;
        }}
        
        .organization {{
            background: #f0f7ff;
            color: #0066cc;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
        }}
        
        .paper-summary {{
            background: #fafafa;
            padding: 16px;
            border-radius: 8px;
            font-size: 14px;
            color: #444;
            line-height: 1.7;
        }}
        
        .paper-summary-label {{
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            display: block;
        }}
        
        .key-points {{
            margin-top: 12px;
        }}
        
        .key-point {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 6px;
            font-size: 14px;
        }}
        
        .key-point::before {{
            content: "•";
            color: #FFD21E;
            font-weight: bold;
        }}
        
        .view-button {{
            display: inline-block;
            margin-top: 12px;
            padding: 8px 16px;
            background: #FFD21E;
            color: #333;
            text-decoration: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.2s;
        }}
        
        .view-button:hover {{
            background: #e6bc0a;
        }}
        
        .footer {{
            text-align: center;
            padding: 24px;
            color: #888;
            font-size: 12px;
        }}
        
        .footer a {{
            color: #FF9D0B;
            text-decoration: none;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #FF9D0B;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤗 Hugging Face Daily Papers</h1>
            <p class="subtitle">오늘의 AI/ML 연구 논문 뉴스레터</p>
            <span class="date-badge">{content.date}</span>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{content.total_count}</div>
                    <div class="stat-label">논문 수</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{sum(p.upvotes for p in content.papers)}</div>
                    <div class="stat-label">총 업보트</div>
                </div>
            </div>
"""
        
        # 논문 카드 추가
        for i, paper in enumerate(content.papers, 1):
            # 저자 표시
            authors_text = ", ".join(paper.korean_authors[:3])
            if len(paper.korean_authors) > 3:
                authors_text += f" 외 {len(paper.korean_authors) - 3}명"
            
            # 조직 표시
            org_html = ""
            if paper.organization:
                org_html = f'<span class="organization">🏢 {paper.organization}</span>'
            
            # 핵심 포인트 HTML
            key_points_html = ""
            if paper.key_points:
                key_points_html = '<div class="key-points">'
                for point in paper.key_points[:3]:
                    key_points_html += f'<div class="key-point">{point}</div>'
                key_points_html += '</div>'
            
            html += f"""
            <div class="paper-card">
                <div style="margin-bottom: 12px;">
                    <span class="paper-number">{i}</span>
                    <span class="paper-title">{paper.korean_title}</span>
                </div>
                <div class="paper-title-en">{paper.original_title}</div>
                
                <div class="paper-meta">
                    <div class="meta-item">
                        <span>👤</span>
                        <span>{authors_text}</span>
                    </div>
                    <div class="meta-item">
                        <span>⬆️</span>
                        <span>{paper.upvotes} upvotes</span>
                    </div>
                    {org_html}
                </div>
                
                <div class="paper-summary">
                    <span class="paper-summary-label">📝 요약</span>
                    {paper.korean_summary}
                    {key_points_html}
                </div>
                
                <a href="{paper.paper_url}" class="view-button">🔗 논문 보기 →</a>
            </div>
"""
        
        # 푸터
        html += f"""
        </div>
        
        <div class="footer">
            <p>
                이 뉴스레터는 Hugging Face Daily Papers를 바탕으로<br>
                자동으로 생성되었습니다.
            </p>
            <p style="margin-top: 8px;">
                <a href="https://huggingface.co/papers">Hugging Face Papers</a> |
                <a href="https://huggingface.co/papers/daily">구독 취소</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def to_text(self, content: NewsletterContent) -> str:
        """텍스트 형식의 뉴스레터 생성"""
        text = f"""
==========================================
🤗 Hugging Face Daily Papers
한국어 뉴스레터
==========================================

📅 {content.date}

📊 오늘의 논문: {content.total_count}개

"""
        
        for i, paper in enumerate(content.papers, 1):
            authors_text = ", ".join(paper.korean_authors[:3])
            if len(paper.korean_authors) > 3:
                authors_text += f" 외 {len(paper.korean_authors) - 3}명"
            
            text += f"""
------------------------------------------
{i}. {paper.korean_title}
------------------------------------------
원어: {paper.original_title}

저자: {authors_text}
업보트: {paper.upvotes}
"""
            if paper.organization:
                text += f"조직: {paper.organization}\n"
            
            text += f"""
요약:
{paper.korean_summary}

링크: {paper.paper_url}
"""
            
            if paper.key_points:
                text += "\n핵심 포인트:\n"
                for point in paper.key_points[:3]:
                    text += f"  • {point}\n"
            
            text += "\n"
        
        text += """
==========================================
Hugging Face Daily Papers에서 더 많은 논문 확인하기:
https://huggingface.co/papers
==========================================
"""
        
        return text


class EmailSender:
    """이메일 발송기"""
    
    def __init__(self, smtp_server: str, smtp_port: int, sender: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.password = password
    
    def send(self, recipients: List[str], subject: str, html_content: str, text_content: str = None) -> bool:
        """이메일 발송"""
        if not recipients:
            print("수신자가 지정되지 않았습니다.")
            return False
        
        try:
            # MIME 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ", ".join(recipients)
            
            # 텍스트 버전 추가
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # HTML 버전 추가
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.sendmail(self.sender, recipients, msg.as_string())
            
            print(f"✅ 이메일이 성공적으로 발송되었습니다!")
            print(f"   수신자: {', '.join(recipients)}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ 이메일 인증에 실패했습니다. 앱 비밀번호를 확인해주세요.")
            return False
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {e}")
            return False
    
    def send_newsletter(self, recipients: List[str], content: NewsletterContent) -> bool:
        """뉴스레터 발송"""
        subject = f"🤗 Hugging Face Daily Papers - {content.date}"
        
        generator = NewsletterGenerator()
        html_content = generator.to_html(content)
        text_content = generator.to_text(content)
        
        return self.send(recipients, subject, html_content, text_content)


# 테스트 코드
if __name__ == "__main__":
    from crawler import HuggingFacePapersCrawler
    
    # 논문 가져오기
    crawler = HuggingFacePapersCrawler()
    papers = crawler.fetch_daily_papers()
    
    if papers:
        # 뉴스레터 생성
        generator = NewsletterGenerator()
        content = generator.generate(papers, max_papers=5)
        
        print(f"✅ {content.total_count}개의 논문으로 뉴스레터 생성 완료!")
        print("\n--- HTML 미리보기 (첫 500자) ---")
        print(generator.to_html(content)[:500])
        
    crawler.close()
