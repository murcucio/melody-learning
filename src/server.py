"""
FastAPI 백엔드 서버: 이미지에서 학습 텍스트 추출, 멜로디 가이드 생성, Mureka 노래 생성 API 제공
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.mureka_utils import find_audio_urls
from src.core.workflow import (
    build_mureka_request,
    create_mnemonic_plan,
    extract_study_text_from_base64,
    request_mureka_song,
)

load_dotenv()

app = FastAPI(title="학습용 멜로디 생성 API")

# CORS 설정: 웹 프론트엔드에서 접근 가능하도록
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractTextRequest(BaseModel):
    image_base64: str


class ExtractTextResponse(BaseModel):
    study_text: str


class MnemonicPlanRequest(BaseModel):
    study_text: str


class MnemonicPlanResponse(BaseModel):
    mnemonic_plan: str


class GenerateSongRequest(BaseModel):
    study_text: str
    mnemonic_plan: str
    wait_for_audio: bool = True


class GenerateSongResponse(BaseModel):
    task_id: Optional[str] = None
    audio_urls: list[str] = []
    status: str = "completed"


def get_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")
    return key


def get_mureka_key() -> Optional[str]:
    return os.getenv("MUREKA_API_KEY")


@app.post("/extract-text", response_model=ExtractTextResponse)
async def extract_text(req: ExtractTextRequest) -> ExtractTextResponse:
    """이미지(base64)에서 학습용 텍스트 추출"""
    try:
        api_key = get_openai_key()
        study_text = extract_study_text_from_base64(req.image_base64, api_key)
        if not study_text.strip():
            raise HTTPException(status_code=400, detail="텍스트를 추출하지 못했습니다.")
        return ExtractTextResponse(study_text=study_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 추출 실패: {str(e)}")


@app.post("/mnemonic-plan", response_model=MnemonicPlanResponse)
async def mnemonic_plan(req: MnemonicPlanRequest) -> MnemonicPlanResponse:
    """학습 텍스트로부터 멜로디 가이드 생성"""
    try:
        api_key = get_openai_key()
        plan = create_mnemonic_plan(req.study_text, api_key)
        return MnemonicPlanResponse(mnemonic_plan=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"멜로디 가이드 생성 실패: {str(e)}")


@app.post("/generate-song", response_model=GenerateSongResponse)
async def generate_song(req: GenerateSongRequest) -> GenerateSongResponse:
    """Mureka API를 사용해 노래 생성"""
    mureka_key = get_mureka_key()
    if not mureka_key:
        raise HTTPException(status_code=500, detail="MUREKA_API_KEY가 설정되지 않았습니다.")

    try:
        payload = build_mureka_request(req.study_text, req.mnemonic_plan)
        result = request_mureka_song(payload, mureka_key, wait=req.wait_for_audio)

        audio_urls = find_audio_urls(result)

        if req.wait_for_audio:
            return GenerateSongResponse(
                task_id=result.get("id"),
                audio_urls=audio_urls,
                status=result.get("status", "completed"),
            )
        else:
            return GenerateSongResponse(
                task_id=result.get("id"),
                audio_urls=[],
                status="pending",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"노래 생성 실패: {str(e)}")


@app.get("/")
async def root() -> Dict[str, Any]:
    """루트 엔드포인트: API 정보 제공"""
    return {
        "message": "학습용 멜로디 생성 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /extract-text": "이미지에서 텍스트 추출",
            "POST /mnemonic-plan": "멜로디 가이드 생성",
            "POST /generate-song": "Mureka 노래 생성",
            "GET /health": "헬스 체크",
        },
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}

