const statusEl = document.getElementById("status");
const backendUrlEl = document.getElementById("backend-url");
const backendBase = window.BACKEND_BASE || "http://localhost:8000";

backendUrlEl.textContent = backendBase;

const generateBtn = document.getElementById("generate-btn");
const imageInput = document.getElementById("image-input");
const waitCheckbox = document.getElementById("wait-audio");
const studyTextEl = document.getElementById("study-text");
const planTextEl = document.getElementById("plan-text");
const audioContainer = document.getElementById("audio-output");

function setStatus(message) {
  statusEl.textContent = message;
}

function setPre(el, value) {
  el.textContent = value?.trim() || "-";
}

function clearAudio() {
  audioContainer.innerHTML = "";
  audioContainer.append("없음");
}

function renderAudio(urls) {
  audioContainer.innerHTML = "";
  if (!urls || urls.length === 0) {
    audioContainer.append("없음");
    return;
  }
  urls.forEach((url) => {
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.src = url;
    audioContainer.appendChild(audio);
  });
}

function disableControls() {
  generateBtn.disabled = true;
  imageInput.disabled = true;
}

function enableControls() {
  generateBtn.disabled = false;
  imageInput.disabled = false;
}

function fileToDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("이미지 파일을 읽을 수 없습니다."));
    reader.readAsDataURL(file);
  });
}

async function postJSON(path, payload) {
  const resp = await fetch(`${backendBase}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${path} 요청 실패 (${resp.status}): ${text}`);
  }

  return resp.json();
}

async function handleGenerate() {
  try {
    disableControls();
    if (!imageInput.files || imageInput.files.length === 0) {
      throw new Error("이미지를 선택해주세요.");
    }

    clearAudio();
    setPre(studyTextEl, "-");
    setPre(planTextEl, "-");

    setStatus("이미지 텍스트 추출 중...");
    const dataUrl = await fileToDataURL(imageInput.files[0]);
    const extract = await postJSON("/extract-text", { image_base64: dataUrl });
    const studyText = extract.study_text?.trim();
    if (!studyText) {
      throw new Error("추출된 텍스트가 없습니다.");
    }
    setPre(studyTextEl, studyText);

    setStatus("멜로디 가이드 생성 중...");
    const planResp = await postJSON("/mnemonic-plan", { study_text: studyText });
    const mnemonicPlan = planResp.mnemonic_plan || "";
    setPre(planTextEl, mnemonicPlan);

    setStatus("Mureka 노래 생성 중...");
    const songResp = await postJSON("/generate-song", {
      study_text: studyText,
      mnemonic_plan: mnemonicPlan,
      wait_for_audio: Boolean(waitCheckbox.checked),
    });
    renderAudio(songResp.audio_urls || []);

    if (songResp.audio_urls && songResp.audio_urls.length > 0) {
      setStatus("완료! 곡을 재생해보세요.");
    } else {
      setStatus("생성 완료. 오디오 URL을 응답에서 찾지 못했습니다.");
    }
  } catch (error) {
    console.error(error);
    setStatus(`에러: ${error.message || error}`);
  } finally {
    enableControls();
  }
}

generateBtn.addEventListener("click", handleGenerate);

