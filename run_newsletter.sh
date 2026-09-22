#!/bin/bash
#===================================
# Hugging Face Daily Papers Newsletter
# Mac/Linux용 자동 실행 스크립트
#===================================

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 로그 파일
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/newsletter_$(date +%Y%m%d_%H%M%S).log"

# 환경 변수 로드
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
fi

echo "========================================"
echo "Hugging Face Daily Papers Newsletter"
echo "실행 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# Python 실행
python3 scheduler.py --output "$SCRIPT_DIR/newsletter" 2>&1 | tee "$LOG_FILE"

# 결과 확인
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo "✅ 뉴스레터 생성 완료!"
    echo "📁 로그 파일: $LOG_FILE"
else
    echo ""
    echo "❌ 오류가 발생했습니다. 로그 파일을 확인해주세요."
    echo "📁 로그 파일: $LOG_FILE"
fi
