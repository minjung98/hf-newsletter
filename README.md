# 🤗 Hugging Face Daily Papers 한국어 뉴스레터

Hugging Face의 일일 AI/ML 연구 논문을 자동으로 가져와 한국어로 번역하고, 이메일로 발송하는 뉴스레터 도구입니다.

## 📋 주요 기능

- **논문 수집**: Hugging Face Daily Papers에서 최신 AI/ML 연구 논문 자동 수집
- **한국어 번역**: AI/ML 전문 용어 사전을 활용한 한국어 번역
- **이메일 발송**: Gmail SMTP를 통한 뉴스레터 자동 발송
- **스케줄링**: Mac/Linux cron 또는 Windows 작업 스케줄러를 통한 자동 실행

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
cd hf_papers_newsletter
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
# 이메일 설정
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # Gmail 앱 비밀번호
EMAIL_RECIPIENTS=recipient1@email.com,recipient2@email.com

# 선택사항: OpenAI 번역 사용 시
OPENAI_API_KEY=your-openai-api-key
```

#### Gmail 앱 비밀번호 생성 방법
1. Google 계정 → 보안 → 2단계 인증 활성화
2. 앱 비밀번호 생성 → 메일 선택 → 비밀번호 복사

### 3. 뉴스레터 미리보기

```bash
# 이메일 발송 없이 미리보기
python scheduler.py --dry-run

# 특정 날짜의 논문 보기
python scheduler.py --date 2024-09-21 --dry-run

# 파일로 저장
python scheduler.py --output newsletter --dry-run
```

### 4. 이메일 발송

```bash
# 즉시 발송
python scheduler.py

# 최대 논문 수 지정
python scheduler.py --max-papers 20
```

## ⚙️ 고급 설정

### OpenAI GPT 번역 사용

기본 번역기는 규칙 기반이며, 더 나은 번역을 원하면:

```bash
# OpenAI API 키 설정 필요
export OPENAI_API_KEY=your-key

# GPT 번역 모드로 실행
python scheduler.py --openai
```

### 자동 스케줄링

#### Mac/Linux (cron)

```bash
# crontab 편집
crontab -e

# 매일 아침 9시에 실행
0 9 * * * cd /path/to/hf_papers_newsletter && /usr/bin/python3 scheduler.py >> /path/to/logs/newsletter.log 2>&1
```

#### Mac (launchd)

`com.hfnewsletter.plist` 파일 생성:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hfnewsletter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/scheduler.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

```bash
# 등록
cp com.hfnewsletter.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.hfnewsletter.plist
```

## 📁 프로젝트 구조

```
hf_papers_newsletter/
├── config.py          # 설정 관리
├── crawler.py         # Hugging Face 논문 크롤링
├── translator.py      # 한국어 번역 모듈
├── newsletter.py     # 뉴스레터 생성 및 이메일 발송
├── scheduler.py      # 메인 실행 스크립트
├── requirements.txt  # Python 의존성
└── README.md         # 이 파일
```

## 🔧 명령줄 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-d, --date` | 날짜 (YYYY-MM-DD) | 오늘 |
| `-n, --max-papers` | 최대 논문 수 | 10 |
| `--dry-run` | 이메일 발송 없이 미리보기 | False |
| `-o, --output` | 출력 파일 경로 | 콘솔 출력 |
| `--openai` | OpenAI GPT 번역 사용 | False |

## 📧 뉴스레터 샘플

생성되는 뉴스레터는 다음과 같은 형식입니다:

```
┌─────────────────────────────────────────┐
│  🤗 Hugging Face Daily Papers           │
│  오늘의 AI/ML 연구 논문 뉴스레터         │
│  2024년 9월 21일                        │
├─────────────────────────────────────────┤
│  📊 오늘의 논문: 10개                    │
│                                         │
│  1. [논문 제목]                          │
│     저자: 홍길동 외 3명                   │
│     조직: Stanford University            │
│     ⬆️ 120 upvotes                      │
│                                         │
│     📝 요약                              │
│     [한국어 번역 요약...]                │
│                                         │
│     핵심 포인트:                          │
│     • 새로운 접근법 제안                   │
│     • 성능 개선 달성                      │
│                                         │
│     [🔗 논문 보기]                       │
├─────────────────────────────────────────┤
│  이 뉴스레터는 HF Daily Papers 기반       │
└─────────────────────────────────────────┘
```

## ❓ 자주 묻는 질문

### Q: Gmail 이메일 서비스 사용 가능?
A: 현재는 Gmail SMTP만 지원합니다. 다른 서비스(SendGrid, Mailgun 등)는 나중에 지원 예정입니다.

### Q: 매일 자동으로 실행하고 싶습니다.
A: 위의 스케줄링 섹션을 참고하여 cron 또는 launchd를 설정하세요.

### Q: 뉴스레터 수신을 중단하고 싶습니다.
A: 아래 명령어로 자동 실행을 해제할 수 있습니다:

```bash
crontab -r
```

이 명령어를 실행하면 매일 7시에 뉴스레터가 전송되지 않습니다. (어떤 경로에서든 터미널에서 실행하면 됨)

## 📝 라이선스

MIT License

## 🤝 기여

버그 리포트 및 기능 요청은 GitHub Issues에 남겨주세요.
