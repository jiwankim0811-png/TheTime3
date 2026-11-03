# ==============================================================================
# Google Cloud Run 배포용 공식 표준 Dockerfile
# ==============================================================================

# 1. 경량화된 안정적인 Python 3.11 슬림 이미지
FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 (Cloud Logging에 실시간 출력)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cloud Run 기본 포트 (런타임에 동적으로 주입됨, 기본값 8080)
ENV PORT=8080

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 시스템 필수 유틸리티 설치 및 apt 캐시 정리
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성 패키지 설치 (빌드 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 소스 코드 전체 복사
COPY . .

# Cloud Run 수신 포트
EXPOSE 8080

# Google Cloud Run 공식 권장 시작 명령:
# Gunicorn을 프로세스 매니저로 두고, Uvicorn Worker를 통해 비동기 FastAPI 앱을 안정적으로 서빙합니다.
# PORT 미설정 시 기본 8080 포트로 바인딩됩니다.
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app
