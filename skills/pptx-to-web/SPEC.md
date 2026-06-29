# SPEC — pptx-to-web Harness Asset

## 목표
PowerPoint(.pptx)를 **콘텐츠 기반 웹사이트**로 변환해 GitHub Pages에 게시한다.
스크린샷이 아니라 실제 콘텐츠(텍스트·이미지·표·영상)를 추출해 HTML/CSS로
재구성한다. 텍스트는 선택·검색 가능해야 한다.

## 입력 / 출력
- 입력: `.pptx` 파일 경로.
- 출력: `docs/`
  - `index.html` — 사이드바 목차 + 세로 스크롤(스냅) 웹 덱
  - `media/…` — 추출된 이미지/영상
  - `deck.json` — 메타(제목, 종횡비, 슬라이드 HTML, 목차 titles)

## 레이아웃 (요구사항)
- 왼쪽 고정 **사이드바**: 슬라이드 번호+제목 목차, 현재 위치 하이라이트, 클릭 이동.
- 오른쪽 본문: 위→아래 **세로 스크롤**, `scroll-snap`으로 한 장씩 정렬.
- 컬러풀: 슬라이드별 그라데이션·광원, 화이트 타이포, 글래스 표, 16:9 카드.

## 변환 파이프라인 (native)
1. python-pptx로 슬라이드별 텍스트런(폰트·크기·색·볼드·정렬)/그림/표 추출.
2. EMU→% 좌표 환산, 폰트 `cqh` 반응형, 어두운 글자색은 화이트 치환.
3. 그림 blob 추출, 표 `<table>`, 외부 링크(YouTube/Vimeo)는 `<iframe>`.
4. 슬라이드 제목 추출 → 사이드바 목차, 한 페이지 SPA로 렌더.

## 대체 모드
- 이미지 모드(`pptx2web.py`): soffice 렌더 + ffmpeg, 룩앤필 1:1, 영상 오버레이.

## 최신 업데이트 (Azure 공식)
- `fetch_updates.py`가 Microsoft Foundry 공식 What's-new(raw md)를 수집 → updates.json.
- `pptx2web_native.py --updates`로 덱 끝에 카테고리별 "최신 업데이트" 슬라이드 추가.

## 충실도/엣지
- 영상 0개·표 0개도 동작, 한글 보존, 50+장 처리, 결정적 출력.

## 배포
- `docs/` + `.nojekyll`, Pages `main /docs` 또는 `pages.yml` 자동 배포.
