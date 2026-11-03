# ==========================================
# Google Cloud Run 배포용 경량 Dockerfile
# ==========================================

# 1. 가볍고 안정적인 Python 3.11 슬림 이미지 사용
FROM python:3.11-slim

# 표준 출력 및 에러 로깅이 즉각 버퍼링 없이 전송되도록 설정 (Cloud Logging 연동 최적화)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cloud Run 기본 포트 환경변수 (런타임에 주입됨, 기본값 8080)
ENV PORT=8080

# 컨테이너 내 작업 디렉토리 지정
WORKDIR /app

# 시스템 의존성 설치 및 캐시 정리
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치 (캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Cloud Run 포트 노출 선언
EXPOSE 8080

# Cloud Run 컨테이너 시작 명령 (Cloud Run이 지정하는 $PORT를 감지하여 실행)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}


