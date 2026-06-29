# pptx-to-web — PowerPoint를 웹 발표 사이트로 만드는 Copilot 스킬

> 하네스톤 2026 · **트랙2** · "GitHub Copilot으로 Harness Asset 만들기"
> **제출물: Copilot Skill** — `.github/skills/pptx-to-web/`

PPTX를 던지면 에이전트가 모든 장표를 보고 **박스·다이어그램으로 재해석한 웹 덱**을 만들어 GitHub Pages에 배포하는, 복붙 가능한 재사용 스킬입니다. 아래 데모는 이 스킬이 자동 생성한 결과물입니다.

🔗 **스킬이 만든 결과 예시:** https://hijigoo.github.io/tech-summit-hanessathon-2026/

## 스킬 구성
| 파일 | 역할 |
|---|---|
| `SKILL.md` | 워크플로우·규칙·컴포넌트 사양 (에이전트가 따르는 단일 명세) |
| `scripts/capture.py` | 모든 장표를 PNG로 캡처 |
| `scripts/pptx2web_native.py` | content.json → 컬러풀 랜드스케이프 HTML 덱 빌드 |
| `scripts/fetch_updates.py` | Azure/Foundry 최신 업데이트 자동 수집·추가 |
| `scripts/verify.js` | headless 렌더로 빈 슬라이드 0 검증 |
| `templates/` | 컴포넌트 예시 + 완성 덱 레퍼런스 |

## 동작 방식 (스킬 하나로 6단계)
1. **캡처** — PPTX 전체를 스크린샷 PNG로
2. **재해석** — 에이전트가 PNG를 보고 발표자 노트 → 박스·도형·플로우로 HTML 작성
3. **최신화** — Azure 공식 "What's new" 자동 추가
4. **빌드** — 목차·1화면 랜드스케이프·6색 테마·발표 노트 덱 생성
5. **검증** — 빈 장표 0 자동 확인
6. **배포** — GitHub Pages

## 왜 1등인가
- **스킬 하나로 끝**: 다른 도구 없이 캡처→배포 전 과정 자동.
- **AI 재해석**: 텍스트 추출이 아닌 화면 이해 → 허브·도넛·막대·팬인 SVG 다이어그램.
- **자가 검증**: 빈 슬라이드 0 보장. **재사용**: 템플릿 복사로 어떤 PPT도 동일 품질.

## 사용
```bash
S=.github/skills/pptx-to-web
pip install -r $S/scripts/requirements.txt
python3 $S/scripts/capture.py deck.pptx --out /tmp/shots
python3 $S/scripts/pptx2web_native.py --content content.json --updates docs/updates.json --out docs
```
