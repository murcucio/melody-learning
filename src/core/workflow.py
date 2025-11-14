from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents import build_mnemonic_plan
from src.compose_prompt import build_mureka_payload
from src.mureka_client import MurekaClient
from src.vision_to_query import image_bytes_to_study_text


def extract_study_text(
    image_bytes: bytes,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> str:
    return image_bytes_to_study_text(image_bytes, api_key, model=model)


def extract_study_text_from_base64(
    image_b64: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> str:
    header, _, data = image_b64.partition(",")
    if data:
        encoded = data
    else:
        encoded = header
    image_bytes = base64.b64decode(encoded)
    return extract_study_text(image_bytes, api_key, model=model)


def create_mnemonic_plan(
    study_text: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> str:
    client = OpenAI(api_key=api_key)
    return build_mnemonic_plan(client, study_text, model=model)


def build_mureka_request(study_text: str, mnemonic_plan: str) -> Dict[str, Any]:
    return build_mureka_payload(mnemonic_plan, study_text)


def request_mureka_song(
    payload: Dict[str, Any],
    api_key: str,
    wait: bool = True,
    **client_kwargs: Any,
) -> Dict[str, Any]:
    client = MurekaClient(api_key=api_key, **client_kwargs)
    if wait:
        return client.generate_and_wait(payload)
    task_id = client.create_song(payload)
    return {"id": task_id}


def run_full_pipeline(
    image_bytes: bytes,
    openai_key: str,
    mureka_key: Optional[str] = None,
    *,
    openai_model: str = "gpt-4o-mini",
    wait_for_audio: bool = True,
    **mureka_kwargs: Any,
) -> Dict[str, Any]:
    study_text = extract_study_text(image_bytes, openai_key, model=openai_model)
    mnemonic_plan = create_mnemonic_plan(study_text, openai_key, model=openai_model)
    payload = build_mureka_request(study_text, mnemonic_plan)

    result: Dict[str, Any] = {
        "study_text": study_text,
        "mnemonic_plan": mnemonic_plan,
        "mureka_payload": payload,
    }

    if mureka_key:
        song_result = request_mureka_song(payload, mureka_key, wait=wait_for_audio, **mureka_kwargs)
        result["mureka_result"] = song_result

    return result

