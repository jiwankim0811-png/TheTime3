# ==============================================================================
# Google Cloud Run 배포용 안정 최적화 Dockerfile
# ==============================================================================

FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 (Cloud Logging 실시간 동기화)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cloud Run 기본 포트
ENV PORT=8080

WORKDIR /app

# 파이썬 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8080

# 쉘 변수 치환 오류를 원천 차단하기 위해 python으로 직접 main.py를 실행합니다.
# main.py 내부에서 os.environ["PORT"]를 읽어 0.0.0.0 포트로 안전하게 바인딩합니다.
CMD ["python", "main.py"]
