# 학습용 멜로디 생성기

이미지에서 학습용 텍스트를 추출하고, 기억하기 쉬운 멜로디 가이드를 생성한 뒤 Mureka API로 노래를 만드는 웹 애플리케이션입니다.

## 설치

### 1. 의존성 설치

```bash
pip install fastapi uvicorn python-dotenv openai requests pydantic
```

또는 `requirements.txt`가 있다면:

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
MUREKA_API_KEY=your_mureka_api_key_here
```

## 실행 방법

### 웹 애플리케이션 실행

#### 1. 백엔드 서버 시작

터미널 1에서:

```bash
cd /Users/baehanjun/PythonProjects/ai-project-2
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

백엔드가 `http://localhost:8000`에서 실행됩니다.

#### 2. 프론트엔드 서버 시작

터미널 2에서:

```bash
cd /Users/baehanjun/PythonProjects/ai-project-2
python3 -m http.server --directory web 3000
```

또는:

```bash
cd web
python3 -m http.server 3000
```

프론트엔드가 `http://localhost:3000`에서 실행됩니다.

#### 3. 브라우저에서 접속

브라우저에서 `http://localhost:3000`을 열고 이미지를 업로드하면 됩니다.

### CLI로 실행

이미지 파일 경로를 직접 지정해서 실행할 수 있습니다:

```bash
python3 src/run_pipeline.py
```

기본 이미지 경로가 하드코딩되어 있으므로, `run_pipeline.py`의 마지막 줄을 수정하거나 명령줄 인자로 받도록 변경할 수 있습니다.

## 프로젝트 구조

```
src/
  ├── server.py          # FastAPI 백엔드 (웹용)
  ├── run_pipeline.py    # CLI 파이프라인
  ├── core/
  │   ├── workflow.py     # 핵심 워크플로우 함수들
  │   └── mureka_utils.py # Mureka 오디오 처리 유틸
  ├── agents.py          # 멜로디 가이드 생성
  ├── compose_prompt.py  # Mureka 페이로드 구성
  ├── mureka_client.py   # Mureka API 클라이언트
  └── vision_to_query.py # 이미지 OCR

web/
  ├── index.html         # 프론트엔드 HTML
  └── main.js            # 순수 JavaScript
```

## API 엔드포인트

- `POST /extract-text`: 이미지(base64)에서 텍스트 추출
- `POST /mnemonic-plan`: 학습 텍스트로 멜로디 가이드 생성
- `POST /generate-song`: Mureka API로 노래 생성
- `GET /health`: 헬스 체크

## 문제 해결

### 429 Too Many Requests 오류

Mureka API의 요청 제한에 걸렸을 수 있습니다. 잠시 기다렸다가 다시 시도하거나, 백엔드의 재시도 로직이 자동으로 처리합니다.

### 모듈을 찾을 수 없다는 오류

프로젝트 루트에서 실행했는지 확인하세요. `PYTHONPATH`가 필요할 수 있습니다:

```bash
export PYTHONPATH=/Users/baehanjun/PythonProjects/ai-project-2:$PYTHONPATH
```

