"""
Google Cloud Run 배포용 정렬 알고리즘 시각화 백엔드 서버 (main.py)
Stitch 연동 프로젝트: projects/16206957468015839200
"""

import os
import sys
from typing import List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

try:
    from algorithms import run_all_sorts
except ImportError:
    from .algorithms import run_all_sorts


app = FastAPI(
    title="Heap & Counting Sort Visualization API",
    description="힙 정렬 및 계수 정렬 실시간 스냅샷 생성 서버 (Google Stitch 연동)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortRequest(BaseModel):
    array: List[int] = Field(
        ...,
        description="정렬할 정수 리스트 (1~60개)",
        examples=[[45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 68, 86]]
    )

    @field_validator("array")
    @classmethod
    def validate_array(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("배열이 비어 있습니다. 최소 1개 이상의 정수를 전달해야 합니다.")
        if len(v) > 60:
            raise ValueError("원활한 시각화를 위해 배열 크기는 최대 60개로 제한됩니다.")
        for item in v:
            if not isinstance(item, int):
                raise ValueError("배열의 모든 요소는 정수여야 합니다.")
        return v


@app.get("/", tags=["General"])
def root():
    return {
        "service": "Heap & Counting Sort Visualization API",
        "status": "healthy",
        "stitchProject": "projects/16206957468015839200",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Monitoring"])
def health():
    return {
        "status": "UP",
        "service": "sorting-visualizer-backend"
    }


@app.get("/api/info", tags=["Algorithm Info"])
def get_algorithm_info():
    return {
        "stitchProject": "projects/16206957468015839200",
        "algorithms": [
            {
                "name": "Heap Sort",
                "koreanName": "힙 정렬",
                "accentColor": "#7bd0ff",
                "timeComplexity": "O(N log N)",
                "spaceComplexity": "O(1)",
                "category": "Comparison Tree Sort"
            },
            {
                "name": "Counting Sort",
                "koreanName": "계수 정렬",
                "accentColor": "#45dfa4",
                "timeComplexity": "O(N + K)",
                "spaceComplexity": "O(N + K)",
                "category": "Non-comparison Distribution Sort"
            }
        ]
    }


@app.post("/api/sort", tags=["Sorting"])
def execute_sort(request: SortRequest):
    try:
        result = run_all_sorts(request.array)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"정렬 스냅샷 생성 중 서버 오류 발생: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Cloud Run 컨테이너 환경의 PORT 환경 변수 감지 (기본값 8080)
    port = int(os.environ.get("PORT", "8080"))
    print(f"[Cloud Run] Starting FastAPI server on 0.0.0.0:{port}", flush=True)
    # 프로덕션 컨테이너에서는 reload=False로 구동하여 충돌 방지
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

