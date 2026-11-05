# ==============================================================================
# Google Cloud Run 배포용 안정 최적화 Dockerfile (server 폴더 기준)
# ==============================================================================

FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 (Cloud Logging 실시간 동기화)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

EXPOSE 8080

# 쉘 변수 치환 오류를 방지하기 위해 python main.py로 직접 구동
CMD ["python", "main.py"]

