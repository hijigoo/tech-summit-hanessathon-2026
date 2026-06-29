# pptx-to-web · PowerPoint를 라이브 웹 덱으로

> 하네스톤 2026 · **트랙2** · "GitHub Copilot으로 Harness Asset 만들기"

**PPTX 한 장만 던지면, 에이전트가 직접 보고 다이어그램으로 재해석한 웹 발표 사이트를 만들어 GitHub Pages에 배포합니다.**
스크린샷 복붙이 아니라, 모든 장표를 캡처 → 에이전트가 보고 → 박스·도형·플로우 차트로 다시 그린 컬러풀한 1화면 랜드스케이프 덱. 빈 슬라이드 0 보장.

🔗 **라이브 데모:** https://hijigoo.github.io/tech-summit-hanessathon-2026/

## 왜 1등인가
- **스킬 하나로 끝**: 캡처 → 재해석 → 최신 업데이트 → 빌드 → 검증 → 배포 전 과정 자동.
- **AI 재해석**: 텍스트 추출이 아닌 스크린샷 이해 → 허브-스포크·도넛·막대·팬인 SVG 다이어그램으로 시각화.
- **자가 검증**: headless 렌더로 빈 장표 0을 보장 (`verify.js`).
- **최신성**: Azure/Foundry 공식 "What's new"를 자동 수집해 덱 끝에 추가.
- **발표자 노트**: 각 슬라이드 아래 스크립트, 좌측 목차, 진행바, 6색 테마.
- **재사용**: 참고 템플릿(`templates/`) 복사 → 어떤 PPT도 동일 품질.

## 한 번에
\`\`\`bash
S=.github/skills/pptx-to-web
pip install -r $S/scripts/requirements.txt          # python-pptx, PyMuPDF (+soffice)
python3 $S/scripts/capture.py deck.pptx --out /tmp/shots          # 1) 장표 PNG
#   2) /tmp/shots/*.png 를 보고 content.json 작성 (templates/ 참고)
python3 $S/scripts/fetch_updates.py --out docs/updates.json       # 3) 최신 업데이트
python3 $S/scripts/pptx2web_native.py --content content.json --updates docs/updates.json --out docs  # 4) 빌드
node $S/scripts/verify.js http://localhost:8765/                  # 5) 빈 슬라이드 0 검증
git add docs && git commit && git push                            # 6) Pages 배포
\`\`\`

## 자산
| 자산 | 위치 | 역할 |
|---|---|---|
| Skill | \`.github/skills/pptx-to-web/\` | 캡처·재해석·검증·배포 전 과정 캡슐화 |
| Templates | \`…/templates/\` | 컴포넌트 예시 + 완성 덱 레퍼런스 |
| Code Review Board | \`.github/skills/harness-code-review/\` + 캔버스 | 보너스: severity 보드 어셋 |

## 심사 포인트
재사용성(복붙형 스킬+템플릿) · 자동화(원커맨드 6단계) · 완성도(다이어그램·검증·라이브).
