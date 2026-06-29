# Harness Asset — AI Code Review Board

> 하네스톤 2026 · 트랙2 심화 · "GitHub Copilot으로 Harness Asset 만들기"

**하네스 엔지니어링(에이전트 기반 개발)**을 위한 재사용 어셋. Copilot 에이전트가
코드를 리뷰하고, 결과를 인터랙티브 칸반 보드로 실시간 시각화합니다.

## 구성 자산
| 자산 | 위치 | 역할 |
|---|---|---|
| Skill | `.github/skills/harness-code-review/` | 리뷰 절차·규칙을 캡슐화한 재사용 스킬 |
| Canvas Extension | `.github/extensions/harness-review-board/` | severity별 보드 UI + 에이전트 액션 (set/add/resolve) |
| Demo | `demo/sample-vuln.js` | 의도적 취약 코드 (데모용) |

## 데모 (3단계)
1. `extensions_reload` 또는 `/clear`로 익스텐션 로드
2. 에이전트에게: **"harness-code-review 스킬로 demo/sample-vuln.js 리뷰해줘"**
3. 보드가 열리고 blocking/warning/info 컬럼에 발견 항목이 실시간 표시 → 수정 시 `resolve` 처리

## 심사 포인트
- **재사용성**: 스킬+캔버스로 어떤 리포에도 복붙 가능한 어셋
- **에이전트 액션**: 에이전트가 보드를 직접 제어 (set_findings/add_finding/resolve_finding)
- **실시간 협업 UI**: SSE 기반 라이브 갱신
