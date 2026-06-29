---
name: pptx-to-web
description: 'Convert a PowerPoint (.pptx) into a colorful, content-based HTML website — reinterprets each slide title/key-points/images/notes into web-native explanation slides (full-slide captures used only for interpretation, but real content screenshots like product UI/demos/charts are embedded as-is; variable height, not pixel-for-pixel), with left sidebar TOC, vertical scroll, images, tables, embedded/YouTube videos, speaker notes below each slide — and append the latest Azure/Foundry official updates, then deploy to GitHub Pages. WHEN — "pptx to web", "파워포인트 웹으로", "ppt를 html로", "발표자료 웹버전", "장표 재해석", "발표 스크립트", "발표자 노트", "최신 업데이트 반영", "deploy slides to pages", "pptx html 변환".'
---

# pptx-to-web

PPTX를 **컬러풀한 콘텐츠 기반 웹사이트**로 변환한다. 모든 장표를 스크린샷으로
캡처 → 에이전트가 직접 보고 → 박스·다이어그램·플로우로 재해석한 HTML 슬라이드로
재구성한다. 왼쪽 목차 사이드바 + 오른쪽 세로 스크롤 원페이지(콘텐츠 높이 가변), 발표자
노트, 최신 Azure 업데이트 자동 추가 → GitHub Pages 배포. **이 스킬 하나로 완성**.

## 한 번에 (요약)
```bash
pip install -r scripts/requirements.txt        # python-pptx, PyMuPDF (+soffice)
python3 scripts/capture.py deck.pptx --out /tmp/shots   # ① PNG 캡처
#   ② /tmp/shots/s01..png 를 view로 보고 content.json 작성(templates/ 참고)
python3 scripts/fetch_updates.py --out docs/updates.json                       # ③ 최신 업데이트
python3 scripts/pptx2web_native.py --content content.json --updates docs/updates.json --out docs  # ④ 빌드
cd docs && python3 -m http.server 8765 &                                          # ⑤ 로컬 서버
cd /tmp && npm i playwright && node <skill>/scripts/verify.js http://localhost:8765/             # ⑤ 검증
git add docs && git commit && git push                                          # ⑥ Pages 배포
```

## 참고 템플릿 (templates/)
- `content.template.json`: 모든 컴포넌트(.gr/.cd/.ic/.flow/.stat/.pill/.tag, SVG 도넛·허브) 예시.
- `example-full.content.json`: 실제 23+6장 완성 덱. 새 덱은 이걸 베끼고 내용만 교체.

## 권장 워크플로우: 스크린샷 → AI 재해석 (content.json) ★ 핵심
가장 완성도 높은 방식. PPTX 텍스트 추출에 의존하지 않고, **모든 슬라이드를
스크린샷(PNG)으로 렌더 → 에이전트가 PNG를 직접 보고 → 슬라이드별 콘텐츠를 손으로
재해석해 `content.json`에 작성 → 빌더가 풀 디자인 카드로 렌더**한다. 빈 페이지 0 보장.

### 1) 전체 장표 PNG 캡처
```bash
brew install --cask libreoffice            # soffice 필요(없을 때만)
pip install -r scripts/requirements.txt    # python-pptx, PyMuPDF
python3 scripts/capture.py <input.pptx> --out /tmp/shots   # s01.png..sNN.png
```
### 2) PNG를 보고 ① 발표자 노트 작성 → ② 노트+스크린샷으로 HTML 작성
3단계 파이프라인: **스크린샷 → 노트 → HTML**. 먼저 각 PNG를 view로 보고 그 장표를
설명하는 **구체적인 발표 스크립트**(4~6문장, 실제 발표하듯)를 쓴다. 그 노트를 근거로 화면 구성을 HTML로 재해석한다.
`/tmp/shots/s01.png`부터 끝까지 **view 도구로 직접 본다**(병렬로 여러 장). 결과를
`sample-pptx/content.json`에 작성:
```json
{"title":"덱 제목","slides":[
  {"title":"표지","divider":true,"note":"발표 스크립트"},
  {"title":"슬라이드 제목","html":"<p class='lead'>요약</p><div class='gr gr3'>…</div>","note":"화면을 설명하는 발표자 노트"},
  {"title":"제품 데모 화면","html":"<p class='lead'>실제 UI는 그대로 보여준다</p>","imgs":["media/demo1.png"],"note":"스크린샷이 있으면 imgs로 임베드"}
]}
```
- **note 먼저**: 스크린샷을 보고 실제 발표자가 말할 **구체적 스크립트**를 쓴다. 단순 한 줄 요약 금지.
  - ① 도입(이 장표가 왜 중요한지) → ② 핵심 포인트 2~3개를 수치·예시와 함께 설명 → ③ 다음 장 연결.
  - 화면에 보이는 숫자·고유명사·관계를 **구체적으로 언급**(예: "1,404개 도구", "GPT-4.1-nano로 라우팅").
  - 청중이 노트만 읽어도 발표가 되도록 4~6문장, 친근한 구어체. 빈 노트·"이 장표는 X입니다" 식 금지.
- **html 다음**: 그 노트가 말하는 구조를 깔끔한 카드/플로우로 재현(슬라이드 전체 캡처 임베드 X, 1:1 복제 X).
  - **단, 설명용 콘텐츠 스크린샷은 그대로 사용**: 슬라이드 안에 제품 UI·데모 화면·실제 차트/그래프·코드처럼 재현 불가한 시각 자료가 있으면, 그 이미지는 추출해 `imgs`로 임베드해 그대로 활용한다(`media/`에 저장). "장표 통째 스크린샷"만 금지이고, 본문의 실제 이미지는 보존이 원칙.
- **divider**: 섹션 표지/타이틀/마무리 → 그라데이션 hero.

> **완전성 원칙(누락 금지)**: 원본 슬라이드의 텍스트는 요약으로 날리지 말고 **빠짐없이** 옮긴다.
> 모든 불릿·수치·고유명사·표·각주·예시를 카드/리스트로 보존. 1화면 강제가 없으니 세로로 길어도 OK.
> "핵심만 3개"로 줄이지 말 것 — 7~10개여도 `.gr3/.gr4`·`ul.cols`·여러 카드로 다 담는다.
> 의심되면 추가 캡처를 다시 view로 확인해 누락 없는지 대조. PPTX > 웹의 정보량이 줄면 안 된다.

### 3) 빌드 + 4) 검증 + 5) 배포
```bash
python3 scripts/pptx2web_native.py --content content.json --updates docs/updates.json --out docs
# headless 검증: 빈 섹션 0 확인(playwright)  →  git push origin main (Pages: docs/)
```

### 재해석 HTML 컴포넌트 (REFLOW 내장 클래스)
| 클래스 | 용도 |
|---|---|
| `.lead` | 슬라이드 첫 요약 문장(큰 회색) |
| `.gr .gr2/.gr3/.gr4` | 2·3·4열 카드 그리드 |
| `.cd` (안에 `h3`/`p`) | 글래스 카드(상단 그라데이션 액센트 바·호버 리프트 자동). `style="--a:#..;--b:#.."`로 색상 |
| `.ic` | 카드 상단 아이콘 칩(이모지) |
| `.flow` + `.cd` | 가로 단계 플로우(카드 사이 → 화살표 자동) |
| `.stat` | 큰 강조 숫자(예: 60%) |
| inline `<svg>` | 다이어그램(허브-스포크/도넛/막대/팬인/분기). 텍스트만 많지 않게 시각화 |
| `<pre class='mermaid'>` | 간단한 흐름/관계는 Mermaid로(다크 테마·CDN 자동). `flowchart LR A-->B-->C` 처럼 5~7노드 이내, 복잡한 건 SVG/카드로 |
| `.pill` / `.tag` | 키워드 알약 / NEW 배지 |
- **공통 셸 자동 제공**: 모든 슬라이드에 섹션 eyebrow(번호·덱명), 타이틀 그라데이션+언더라인,
  배경 그리드, 스크롤-인 등장 애니메이션이 빌더에서 자동 적용된다(HTML에 따로 쓰지 말 것).
- **Mermaid는 간단한 것만**: 선형 단계(A→B→C), 분기·병합, 짧은 사이클(루프)에 한해 `mermaid` 블록을
  쓰고, 다이어그램 밑에 `.gr/.cd` 카드로 각 단계 디테일을 함께 싣는다. 노드 7개 초과·중첩 구조는 SVG로.
- **다이어그램 + 디테일 병행**: 구조·흐름·비교는 inline SVG로 그리되(원형 허브, 도넛, 막대, fan-in,
  분기), **다이어그램 아래 카드/리스트로 원본 텍스트·수치·설명을 모두 함께 싣는다**(다이어그램으로
  대체해 본문을 생략하지 말 것). 그라데이션 `id='h'`(시안→퍼플) 재사용.
- 6색 테마는 슬라이드 순서대로 자동 로테이션. 카드별 `--a/--b`로 개별 지정 가능.
- 끝에 최신 Azure/Foundry 업데이트 슬라이드 자동 추가. 항목 많으면 그대로 세로로 흘려 다 보여줌.

## 자동 변환 (재해석 reflow)
```bash
pip install -r scripts/requirements.txt   # python-pptx, PyMuPDF, soffice
python3 scripts/pptx2web_native.py <input.pptx> --out docs --reflow --updates docs/updates.json
```
- 슬라이드를 **스크린샷으로 보지 않고/넣지 않고**, 제목·핵심 포인트·실제 이미지·
  발표 노트를 추출해 **순수 HTML 설명 슬라이드로 재구성**한다(1:1 복제·고정 비율 X).
  장표 전체 캡처는 해석 참고용일 뿐 넣지 않지만, **슬라이드 안의 설명용 콘텐츠 이미지(제품 UI·데모·차트)는 추출해 그대로 임베드**한다. 비어있는 장표는 노트로 채움.
- 좌측 큰 제목 + 핵심 bullet, 우측 슬라이드 내 실제 이미지/영상, 아래 발표 스크립트. 높이 가변.
- 텍스트 선택·검색 가능, 슬라이드별 제목 자동 목차, 끝에 최신 업데이트 슬라이드.
- 출력: `docs/index.html`, `docs/media/*`, `docs/deck.json`.

## 절대배치 변환 (원본 레이아웃 모사)
```bash
python3 scripts/pptx2web_native.py <input.pptx> --out docs
```
- 텍스트 선택·검색 가능, 이미지/표/YouTube 임베드, 슬라이드별 제목 자동 목차.
- 각 슬라이드 아래 **발표 스크립트**(PPTX 발표자 노트) 표시(있을 때만).
- 출력: `docs/index.html`, `docs/media/*`, `docs/deck.json`.

## UI/디자인 (reflow)
- **왼쪽 사이드바**: 번호+제목 목차, 현재 슬라이드 자동 하이라이트, 클릭 시 스크롤.
- **오른쪽 본문**: 세로 스크롤(snap), 상단 스크롤 진행바, 떠다니는 메시 그라데이션 배경.
- **AOS 같은 스크롤-숨김 라이브러리는 쓰지 않는다**(커스텀 스크롤 컨테이너에서 트리거 실패→백지). CSS-only 등장 효과만(섹션이 뷰포트에 들면 `.in` 토글로 reveal).
- 글래스모피즘 카드(블러·상단 액센트 바·호버 리프트), 그라데이션 제목+언더라인, 섹션 eyebrow, 배경 그리드, 6색 테마 로테이션, Sora+Noto Sans KR 폰트.
- 외부 라이브러리는 CDN(빌드 불필요), 16:9 비고정·높이 가변. 빌드 후 헤드리스로 렌더 검증.
- **랜드스케이프(권장, 강제 아님)**: 슬라이드 1:1 화면에 집착하지 말 것. 기본은 **세로로 흐르는
  원페이지 설명형 HTML** — 콘텐츠 높이대로 자연스럽게 흐르고, snap은 proximity(부드러운 정렬)만.
  항목이 많으면 자동 2~3단 컬럼. 한 화면에 욱여넣어 잘리는 것보다 넉넉히 설명하는 게 우선.

## 변환 규칙 (native)
1. python-pptx로 텍스트런(폰트크기·색·볼드·정렬), 그림, 표를 추출.
2. EMU 좌표를 슬라이드 대비 %로 환산해 absolute 배치, 폰트는 `cqh` 반응형.
3. 그림은 blob 추출, 표는 `<table>`, 어두운 글자색은 화이트로 치환(가독성).
4. 슬라이드 rels의 외부 링크(YouTube/Vimeo)는 `<iframe>`으로 임베드.
5. 슬라이드 제목 = 첫 텍스트(공백/제어문자 정리) → 사이드바 목차.
6. 발표자 노트(`notes_slide`)를 추출해 슬라이드 카드 아래 "발표 스크립트"로 표시.

## 빈 슬라이드 방지 (reflow 필수)
다이어그램·SmartArt·그룹 도형 슬라이드는 텍스트 추출이 비어 보일 수 있다. reflow는:
1. **그룹 재귀**: 그룹 안 도형까지 텍스트·이미지를 추출(`_walk`). 작은 아이콘/로고는 제외.
2. **노트 본문화**: 포인트가 0이면 발표 노트를 문장 단위로 쪼개 본문 bullet로 승격.
3. **HTML 디바이더**: 텍스트·이미지·영상·노트가 모두 없는 구분 슬라이드는
   스크린샷을 넣지 않고 그라데이션 HTML 디바이더(섹션 제목)로 재해석한다.
4. **자동 검증**: 빌드 끝에 모든 카드에 본문(포인트/이미지/영상/HTML)이 있는지 확인,
   비면 `WARN: empty slides:[..]` 출력 → 어떤 입력이든 빈 페이지 0 보장.
5. **렌더 검증(권장)**: 배포 전 headless(Playwright)로 각 섹션 `opacity`·높이·본문 수를
   확인해 백지 슬라이드가 없는지 직접 확인한다. content.json 모드에도 동일 적용:
```bash
cd /tmp && npm i playwright && npx playwright install chromium
node -e "const{chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.setViewportSize({width:1366,height:768});await p.goto('http://localhost:8765/');const s=await p.\$\$('section');let e=[];for(let i=0;i<s.length;i++){await s[i].scrollIntoViewIfNeeded();await p.waitForTimeout(120);if((await s[i].innerText()).replace(/\s/g,'').length<8)e.push(i+1);}console.log('empty:',e);await b.close();})()"
```

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
