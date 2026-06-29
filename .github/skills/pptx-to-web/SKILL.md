---
name: pptx-to-web
description: Convert a PowerPoint (.pptx) into a colorful, content-based HTML website — screenshots each slide then reinterprets title/key-points/notes into a web-native layout (variable height, not pixel-for-pixel), with left sidebar TOC, vertical scroll, images, tables, embedded/YouTube videos, speaker notes below each slide — and append the latest Azure/Foundry official updates, then deploy to GitHub Pages. WHEN: "pptx to web", "파워포인트 웹으로", "ppt를 html로", "발표자료 웹버전", "장표 재해석", "발표 스크립트", "발표자 노트", "최신 업데이트 반영", "deploy slides to pages", "pptx html 변환".
---

# pptx-to-web

PPTX를 **콘텐츠 기반 웹사이트**로 변환한다. 스크린샷이 아니라 슬라이드 안의
텍스트·이미지·표·영상을 추출해 진짜 HTML/CSS로 재구성한다. 결과는 왼쪽 목차
사이드바 + 오른쪽 세로 스크롤(스냅) 형태의 컬러풀한 정적 사이트이며 GitHub
Pages에 게시한다.

## 기본 변환 (권장: 재해석 reflow)
```bash
pip install -r scripts/requirements.txt   # python-pptx, PyMuPDF, soffice
python3 scripts/pptx2web_native.py <input.pptx> --out docs --reflow --updates docs/updates.json
```
- 각 슬라이드를 **스크린샷(PNG)** 으로 캡처 + 제목·핵심 포인트·발표 노트를 추출해
  **웹에 맞게 재해석**한다(1:1 복제·고정 비율 X). 비어있는 장표는 노트로 설명을 채운다.
- 좌측 큰 제목 + 핵심 bullet, 우측 슬라이드 캡처/영상, 아래 발표 스크립트. 높이 가변.
- 텍스트 선택·검색 가능, 슬라이드별 제목 자동 목차, 끝에 최신 업데이트 슬라이드.
- 출력: `docs/index.html`, `docs/media/*`, `docs/deck.json`.

## 절대배치 변환 (원본 레이아웃 모사)
```bash
python3 scripts/pptx2web_native.py <input.pptx> --out docs
```
- 텍스트 선택·검색 가능, 이미지/표/YouTube 임베드, 슬라이드별 제목 자동 목차.
- 각 슬라이드 아래 **발표 스크립트**(PPTX 발표자 노트) 표시(있을 때만).
- 출력: `docs/index.html`, `docs/media/*`, `docs/deck.json`.

## UI/디자인
- **왼쪽 사이드바**: 번호+제목 목차, 현재 슬라이드 자동 하이라이트, 클릭 시 스크롤.
- **오른쪽 본문**: 위→아래 세로 스크롤, `scroll-snap`으로 한 장씩 정렬.
- 슬라이드별 그라데이션 배경(6테마 로테이션), 화이트 타이포, 글래스 표,
  컬러 진행감, 16:9 카드, 모바일 사이드바 축소. 한글 웹폰트(Noto Sans KR).

## 변환 규칙 (native)
1. python-pptx로 텍스트런(폰트크기·색·볼드·정렬), 그림, 표를 추출.
2. EMU 좌표를 슬라이드 대비 %로 환산해 absolute 배치, 폰트는 `cqh` 반응형.
3. 그림은 blob 추출, 표는 `<table>`, 어두운 글자색은 화이트로 치환(가독성).
4. 슬라이드 rels의 외부 링크(YouTube/Vimeo)는 `<iframe>`으로 임베드.
5. 슬라이드 제목 = 첫 텍스트(공백/제어문자 정리) → 사이드바 목차.
6. 발표자 노트(`notes_slide`)를 추출해 슬라이드 카드 아래 "발표 스크립트"로 표시.

## 최신 업데이트 자동 추가 (Azure 공식)
발표 내용이 최신 상태를 유지하도록, Azure/Microsoft Foundry 공식 "What's new"를
가져와 덱 끝에 "최신 업데이트" 슬라이드로 추가한다.
```bash
python3 scripts/fetch_updates.py --out docs/updates.json   # 공식 docs에서 수집
python3 scripts/pptx2web_native.py <input.pptx> --out docs --updates docs/updates.json
```
- 출처: Microsoft Foundry 공식 docs(raw md). `--url`로 다른 제품 페이지 지정 가능.
- 카테고리별(예: Azure OpenAI, Foundry Agent Service) 신규 항목을 슬라이드화.

## 이미지 모드 (룩앤필 1:1, 텍스트는 이미지)
원본 디자인을 픽셀 그대로 보존하고 영상을 오버레이하려면:
```bash
python3 scripts/pptx2web.py <input.pptx> --out docs --scale 2.0   # soffice+ffmpeg 필요
```

## GitHub Pages 배포
- Pages를 `main /docs`로 설정하거나 `.github/workflows/pages.yml`로 자동 배포.
- `docs/.nojekyll` 포함. 변환 후 `git push`만 하면 갱신.

## 검증 체크리스트
- 슬라이드 수=원본, 한글 보존, 목차 동기화, 표/이미지/유튜브 표시, 영상 0개도 OK.
