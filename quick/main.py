"""
Google Cloud Run 배포용 정렬 알고리즘 시각화 백엔드 서버 (main.py)

FastAPI 프레임워크를 기반으로 하며, 클라이언트의 정렬 요청을 받아
셸 정렬(Shell Sort), 퀵 정렬(Quick Sort), 병합 정렬(Merge Sort)의
스냅샷 히스토리를 반환합니다.

주요 엔드포인트:
- GET  /             : 서버 기본 상태 및 웰컴 메시지
- GET  /health       : Cloud Run 헬스체크 프로브 엔드포인트
- GET  /api/info     : 지원 알고리즘 목록 및 이론적 시간/공간 복잡도 안내
- POST /api/sort     : 입력 배열에 대해 3가지 알고리즘 실행 및 스냅샷 히스토리 반환
"""

import os
import sys
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# 동일 디렉토리 모듈 임포트
try:
    from algorithms import run_all_sorts
except ImportError:
    from .algorithms import run_all_sorts


# FastAPI 인스턴스 생성
app = FastAPI(
    title="Algorithm Visualization API (Cloud Run)",
    description="셸 정렬, 퀵 정렬, 병합 정렬의 상태 스냅샷 히스토리 생성 서버",
    version="1.0.0"
)

# CORS 설정: 브라우저 및 Google Apps Script(GAS) 환경에서의 자유로운 통신 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션 필요에 따라 특정 도메인으로 한정 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortRequest(BaseModel):
    """정렬 요청 바디 스키마 및 검증"""
    array: List[int] = Field(
        ...,
        description="정렬할 정수 리스트 (최소 1개, 최대 50개 권장)",
        examples=[[38, 27, 43, 3, 9, 82, 10]]
    )

    @field_validator("array")
    @classmethod
    def validate_array_constraints(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("배열이 비어 있습니다. 최소 1개 이상의 정수를 입력해야 합니다.")
        if len(v) > 60:
            raise ValueError("실시간 시각화 애니메이션의 최적 성능을 위해 배열 크기는 최대 60개로 제한됩니다.")
        for item in v:
            if not isinstance(item, int):
                raise ValueError(f"유효하지 않은 데이터 '{item}': 모든 원소는 정수형이어야 합니다.")
            if abs(item) > 10000:
                raise ValueError(f"원소 값 '{item}'이 너무 큽니다. -10,000 ~ 10,000 범위 내의 정수를 입력해주세요.")
        return v


@app.get("/", summary="서버 루트 상태 확인")
async def root():
    """서버 기본 상태 확인 및 가이드 링크"""
    return {
        "status": "online",
        "service": "Algorithm Sorting Visualizer API",
        "environment": "Google Cloud Run / Local",
        "supported_algorithms": ["Shell Sort", "Quick Sort", "Merge Sort"],
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health", summary="헬스체크")
async def health_check():
    """Google Cloud Run Liveness & Readiness 프로브용 헬스체크"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "python_version": sys.version
    }


@app.get("/api/info", summary="알고리즘 복잡도 및 메타데이터")
async def get_algorithms_info():
    """지원하는 3가지 정렬 알고리즘의 복잡도 및 특징 정보 제공"""
    return {
        "algorithms": {
            "shell_sort": {
                "name": "Shell Sort",
                "name_ko": "셸 정렬",
                "inventor": "Donald Shell (1959)",
                "description": "삽입 정렬의 장점을 살리고 단점을 보완한 알고리즘으로, 일정 간격(Gap)만큼 떨어진 요소들을 먼저 정렬해나가는 방식입니다.",
                "complexity": {
                    "time_best": "O(N log N)",
                    "time_avg": "O(N^1.25) ~ O(N^1.5)",
                    "time_worst": "O(N^2)",
                    "space": "O(1) (제자리 정렬)",
                    "stable": False
                }
            },
            "quick_sort": {
                "name": "Quick Sort",
                "name_ko": "퀵 정렬",
                "inventor": "Tony Hoare (1959)",
                "description": "분할 정복(Divide and Conquer) 기법을 사용하여 피벗(Pivot)을 기준으로 작은 값과 큰 값을 분할 배치하는 대표적인 고속 정렬 알고리즘입니다.",
                "complexity": {
                    "time_best": "O(N log N)",
                    "time_avg": "O(N log N)",
                    "time_worst": "O(N^2) (이미 정렬되어 있거나 피벗이 극단적인 경우)",
                    "space": "O(log N) (재귀 호출 스택)",
                    "stable": False
                }
            },
            "merge_sort": {
                "name": "Merge Sort",
                "name_ko": "병합 정렬",
                "inventor": "John von Neumann (1945)",
                "description": "배열을 더 이상 나눌 수 없을 때까지 절반으로 분할한 후, 정렬하면서 다시 결합(Merge)해 나가는 안정적인 분할 정복 알고리즘입니다.",
                "complexity": {
                    "time_best": "O(N log N)",
                    "time_avg": "O(N log N)",
                    "time_worst": "O(N log N)",
                    "space": "O(N) (추가 임시 배열 필요)",
                    "stable": True
                }
            }
        }
    }


@app.post("/api/sort", summary="정렬 상태 스냅샷 히스토리 생성")
async def sort_array(request: SortRequest):
    """
    전달받은 배열에 대해 3가지 알고리즘을 각각 실행하고,
    동일 타임라인에서 스트리밍 애니메이션으로 재생할 수 있는 스냅샷 히스토리를 반환합니다.
    """
    try:
        start_time = time.perf_counter()
        result = run_all_sorts(request.array)
        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 3)
        
        result["server_execution_time_ms"] = execution_time_ms
        result["status"] = "success"
        return result
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"입력값 오류: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 처리 중 오류가 발생했습니다: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """예상치 못한 예외 처리 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "서버 처리 중 예상치 못한 에러가 발생했습니다.",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    # Cloud Run 및 컨테이너 환경의 PORT 환경 변수 지원 (기본 8080)
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


