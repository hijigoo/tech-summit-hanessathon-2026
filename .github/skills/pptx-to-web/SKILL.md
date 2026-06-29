---
name: pptx-to-web
description: Convert a PowerPoint (.pptx) into a static HTML deck that preserves the original look-and-feel, plays embedded videos, and deploys to GitHub Pages. WHEN: "pptx to web", "파워포인트 웹으로", "ppt를 html로", "발표자료 웹버전", "deploy slides to pages", "pptx html 변환".
---

# pptx-to-web

PPTX를 GitHub Pages용 정적 HTML 덱으로 변환한다. 원본 룩앤필을 그대로
보존하고, 임베디드 동영상은 브라우저에서 재생되도록 변환·오버레이한다.

## 요구 도구
- `soffice` (LibreOffice) — 슬라이드 고충실도 렌더
- python: `python-pptx`, `PyMuPDF` (`pip install -r scripts/requirements.txt`)
- `ffmpeg` (선택) — .mov 등 비호환 코덱을 mp4로 변환

## 사용법
콘텐츠 기반(권장, 텍스트 선택가능·웹 네이티브):
```bash
python3 scripts/pptx2web_native.py <input.pptx> --out docs
```
이미지 기반(룩앤필 1:1 보존, 텍스트는 이미지):
```bash
python3 scripts/pptx2web.py <input.pptx> --out docs --scale 2.0
```
- `docs/index.html` 덱, `docs/slides/*.png`, `docs/media/*`, `docs/deck.json` 생성.
- 슬라이드 ←/→·스페이스·클릭 이동, `f` 풀스크린, 하단 진행바.

## 동작
1. soffice로 pptx→pdf, PyMuPDF로 페이지를 2배율 PNG(룩앤필 보존).
2. python-pptx로 슬라이드 크기 + 영상 shape 비율좌표 추출.
3. zip에서 영상/오디오 추출, 비호환 코덱은 ffmpeg로 mp4 변환.
4. 슬라이드 = 이미지 배경 + 영상 위치에 `<video>` 절대배치 오버레이.

## 동작 (native, 콘텐츠 기반)
1. python-pptx로 텍스트런(폰트·크기·색·정렬), 그림, 표를 추출.
2. EMU 좌표를 %로 환산해 absolute 배치, 폰트 크기는 `cqh`로 반응형.
3. 그림은 blob 추출, 표는 `<table>`, 온라인 영상(YouTube)은 `<iframe>`.
4. 텍스트가 실제 HTML이라 선택·검색·SEO·접근성 확보.

## GitHub Pages 배포
- 출력 폴더를 `docs/`로 두고 Pages를 main /docs로 설정하거나,
  `.github/workflows/pages.yml`로 자동 배포.
- `docs/.nojekyll`가 있어 `_`/대용량 에셋도 그대로 서빙.

## 검증 체크리스트
- 슬라이드 수 = 원본, 한글 폰트 보존, 영상 슬라이드 재생, 50+장 OK, 영상 0개도 OK.
